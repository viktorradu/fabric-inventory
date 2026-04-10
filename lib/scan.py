from .client import Client

class Scan:
    def __init__(self, client: Client):
        self.client = client

    def list_workspaces(self) -> list:
        workspaces = self.client.get('v1.0/myorg/admin/workspaces/modified?excludePersonalWorkspaces=True')    
        return workspaces

    def list_workspaces_by_capacities(self, capacity_ids: list) -> list:
        """List workspaces for specific capacities using Fabric Admin API."""
        all_workspaces = []
        for capacity_id in capacity_ids:
            continuation_token = None
            while True:
                url = f"v1/admin/workspaces?capacityId={capacity_id}&state=Active"
                if continuation_token:
                    url += f"&continuationToken={continuation_token}"
                
                workspaces = self.client.get(url)
                if not isinstance(workspaces, dict):
                    print(f"Warning: Unexpected response while retrieving capacity {capacity_id}")
                    break

                if workspaces.get('error'):
                    print(f"Warning: Could not retrieve workspaces for capacity {capacity_id}")
                    break

                workspace_list = workspaces.get('workspaces', [])
                if not isinstance(workspace_list, list):
                    print(f"Warning: Unexpected workspace list format for capacity {capacity_id}")
                    break
                all_workspaces.extend(workspace_list)

                continuation_token = workspaces.get('continuationToken')
                if not continuation_token:
                    break
        return all_workspaces

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
                    ds['createdDate'] = model.get('createdDate')
                    ds['datasources'] = [usage.get('datasourceInstanceId') for usage in model.get('datasourceUsages', [])]

                for flow in workspace.get('dataflows', []):
                    ds = {}
                    result['dataflows'].append(ds)
                    ds['workspaceId'] = workspace.get('id')
                    ds['id'] = flow.get('id')
                    ds['name'] = flow.get('name')
                    ds['createdDate'] = flow.get('createdDate')
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
                