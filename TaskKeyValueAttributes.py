# Copyright 2021, Tertiary Education and Research Network of South Africa
from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule
from ansiblelint.constants import PLAYBOOK_TASK_KEYWORDS, ANNOTATION_KEYS, LINE_NUMBER_KEY, INCLUSION_ACTION_NAMES, ROLE_IMPORT_ACTION_NAMES

if TYPE_CHECKING:
    from typing import Any
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable

'''
Attempt to find the old key=value form of tasks
'''
class TaskKeyValueAttributes(AnsibleLintRule):
    id = 'tenet'
    shortdesc = 'Uses legacy key=value attribute format'
    description = (
        'The old key=value attribute format makes tasks '
        'difficult to read and debug. Consider using a YAML dict'
    )
    severity = 'LOW'
    tags = ['formatting']
    version_added = 'v4.3.7'

    keyvalue_regex = re.compile(r"(?:\s+|^)[^=]+=[^=]+(?:\s+|$)")

    VALID_KEYS = [
        'name', 'action', 'when', 'async', 'poll', 'notify', 'first_available_file', 'include',
        'include_tasks', 'import_tasks', 'import_playbook', 'tags', 'register', 'ignore_errors',
        'delegate_to', 'local_action', 'transport', 'remote_user', 'sudo', 'sudo_user',
        'sudo_pass', 'when', 'connection', 'environment', 'args', 'any_errors_fatal',
        'changed_when', 'failed_when', 'check_mode', 'delay', 'retries', 'until', 'su',
        'su_user', 'su_pass', 'no_log', 'run_once', 'become', 'become_user', 'become_method',
    ]

    def matchplay(self, file: Lintable, play: dict[str, Any]) -> list[MatchError]:
        errors = []
        if not file.kind in PLAYBOOK_TASK_KEYWORDS:
            return []

        if isinstance(play, dict):
            if 'block' in play:
                self.matchplay(file, play['block'])
            elif 'tasks' in play:
                self.matchplay(file, play['tasks'])
            else:
                for k, v in play.items():
                    if (k in self.VALID_KEYS
                            or k in ANNOTATION_KEYS
                            or k in INCLUSION_ACTION_NAMES
                            or k in ROLE_IMPORT_ACTION_NAMES
                        ):
                        continue
                    elif k in ['set_fact']:
                        continue
                    elif k.startswith("with_"):
                        continue
                    elif not isinstance(play[k], str):
                        continue
                    if self.keyvalue_regex.match(play[k]):
                        errors.append(
                            self.create_matcherror(
                                message=self.shortdesc,
                                filename=file,
                                tag=f"{self.id}[keyvalue]",
                                details=f"{k}: {v}",
                                linenumber=play[LINE_NUMBER_KEY],
                            )
                        )

        if isinstance(play, list):
            for play_item in play:
                sub_errors = self.matchplay(file, play_item)
                if sub_errors:
                    errors = errors + sub_errors

        return errors
