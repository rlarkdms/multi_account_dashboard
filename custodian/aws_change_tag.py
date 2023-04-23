
import re
from c7n.actions import Action
from c7n.registry import PluginRegistry

actions = PluginRegistry('custodian.actions')

@actions.register('tag-resource')
class TagResource(Action):
    schema = {
        'type': 'object',
        'properties': {
            'type': {'enum': ['tag-resource']}
        }
    }

    def process(self, resources):
        for resource in resources:
            name = resource['Name']
            tags = resource.get('Tags', [])

            # 리소스 이름에서 cz-project, cz-service 추출
            project_service_pattern = r'^(\w+)-(\w+)-'
            match = re.search(project_service_pattern, name)

            if match:
                tags.append({'Key': 'cz-project', 'Value': match.group(1)})
                tags.append({'Key': 'cz-service', 'Value': match.group(2)})

            # cz-stage 추출
            stage_pattern = r'(dev|qa|stg|prd|prod)'
            match = re.search(stage_pattern, name)

            if match:
                tags.append({'Key': 'cz-stage', 'Value': match.group(1)})

            resource['Tags'] = tags