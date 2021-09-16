# Copyright 2021, Tertiary Education and Research Network of South Africa
import ansiblelint.utils
from ansiblelint.rules import AnsibleLintRule
import re

'''
Attempt to find the old key=value form of tasks
'''
class TaskKeyValueAttributes(AnsibleLintRule):
    id = 'tenet-keyvalue'
    shortdesc = 'Uses legacy key=value attribute format'
    description = (
        'The old key=value attribute format makes tasks '
        'difficult to read and debug. Consider using a YAML dict'
    )
    severity = 'LOW'
    tags = ['tenet']
    version_added = 'v4.3.7'

    keyvalue_regex = re.compile(r"(?:\s+|^)[^=]+=[^=]+(?:\s+|$)")

    def matchplay(self, file, play):
        errors = []
        if not file['type'] in ['tasks', 'handlers']:
            return False

        if isinstance(play, dict):
            if 'block' in play:
                self.matchplay(file, play['block'])
            elif 'tasks' in play:
                self.matchplay(file, play['tasks'])
            else:
                for k, v in play.items():
                    if k in ansiblelint.utils.VALID_KEYS:
                        continue
                    elif k in ['skipped_rules', '__ansible_action_type__', ansiblelint.utils.LINE_NUMBER_KEY, ansiblelint.utils.FILENAME_KEY]:
                        continue
                    elif k in ['set_fact']:
                        continue
                    elif k.startswith("with_"):
                        continue
                    elif k.startswith("include_") or k.startswith("import_"):
                        continue
                    elif not isinstance(play[k], str):
                        continue
                    if self.keyvalue_regex.match(play[k]):
                        errors.append((k + ": " + play[k], self.shortdesc))

        if isinstance(play, list):
            for play_item in play:
                sub_errors = self.matchplay(file, play_item)
                if sub_errors:
                    errors = errors + sub_errors

        return errors
