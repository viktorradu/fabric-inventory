from .client import Client

class Scan:
    def __init__(self, client: Client):
        self.client = client

    def list_workspaces(self) -> list:
        workspaces = self.client.get('v1.0/myorg/admin/workspaces/modified?excludePersonalWorkspaces=True')    
        return workspaces

    def scan_workspaces(self, workspace_ids: list) -> list:
        workspace_list = '","'.join(workspace_ids)
        body = f'{{"workspaces":["{workspace_list}"]}}'
        scanUrl = 'v1.0/myorg/admin/workspaces/getInfo?lineage=True&datasourceDetails=True&getArtifactUsers=true'
        scanInfo = self.client.post(scanUrl, data=body, additional_headers={"Content-Type": "application/json"})
        if not hasattr(scanInfo, 'error'):
            while True:
                scanStatus = self.client.get(f'v1.0/myorg/admin/workspaces/scanStatus/{scanInfo["id"]}')
                if scanStatus.get('status') == 'Succeeded':
                    break

            scanResult = self.client.get(f'v1.0/myorg/admin/workspaces/scanResult/{scanInfo["id"]}')

            result = {'workspaces': [], 'users': [], 'models': [], 'dataflows': [], 'datasources': []}
            for workspace in scanResult.get('workspaces'):
                ws = {}
                result['workspaces'].append(ws)
                ws['id'] = workspace.get('id')
                ws['name'] = workspace.get('name')
                ws['state'] = workspace.get('state')
                ws['capacityId'] = workspace.get('capacityId')
                for model in workspace.get('datasets', []):
                    ds = {}
                    result['models'].append(ds)
                    ds['workspaceId'] = workspace.get('id')
                    ds['id'] = model.get('id')
                    ds['name'] = model.get('name')
                    ds['datasources'] = [usage.get('datasourceInstanceId') for usage in model.get('datasourceUsages', [])]

                for flow in workspace.get('dataflows', []):
                    ds = {}
                    result['dataflows'].append(ds)
                    ds['workspaceId'] = workspace.get('id')
                    ds['id'] = flow.get('id')
                    ds['name'] = flow.get('name')
                    ds['datasources'] = [usage.get('datasourceInstanceId') for usage in flow.get('datasourceUsages', [])]

                users = workspace.get('users', [])
                for user in users if users is not None else []:
                    u = {}
                    result['users'].append(u)
                    u['workspaceId'] = workspace.get('id')
                    u['groupUserAccessRight'] = user.get('groupUserAccessRight')
                    u['identifier'] = user.get('identifier')
                    u['principalType'] = user.get('principalType')
                    u['displayName'] = user.get('displayName')
                
            for datasource in scanResult.get('datasourceInstances', []):
                dsi = {}
                result['datasources'].append(dsi)
                dsi['datasourceType'] = datasource.get('datasourceType')
                dsi['connectionDetails'] = datasource.get('connectionDetails')
                dsi['gatewayId'] = datasource.get('gatewayId')
                dsi['datasourceId'] = datasource.get('datasourceId')
            
            return result
                