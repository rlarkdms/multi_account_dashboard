import json

# Load the tagging rules
with open("key-value-pairs.json", "r") as f:
    tagging_rules = json.load(f)

# Create the Cloud Custodian policy with dynamic filters
policy_template = '''
policies:
  - name: tag-resource-{stage}
    resource: aws.ec2
    filters:
      - "tag:Name": "{stage}"
    actions:
      - type: tag
        key: "cz-stage"
        value: "{stage}"
'''

policies = []
for stage in tagging_rules['stage_tags'].values():
    policies.append(policy_template.format(stage=stage))

# Save the generated policy to a YAML file
with open("custodian_policy.yml", "w") as f:
    f.write(''.join(policies))

print("custodian_policy.yml has been generated")