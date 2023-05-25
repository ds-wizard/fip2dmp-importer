import jinja2
import typing


class _MappingExecutor:

    def __init__(self, project: dict):
        self.project = project
        self.result = []
        self.variables = {}
        self.j2_env = jinja2.Environment(loader=jinja2.BaseLoader())

    def reset(self):
        self.result = []
        self.variables = {}

    def render_jinja2(self, template: str, **kwargs) -> str:
        j2_template = self.j2_env.from_string(template)
        return j2_template.render(
            **self.variables,
            **kwargs,
            _ctx=self.project,
            _result=self.result,
        )

    def get_entity(self, entity_type: str, entity_uuid: str):
        return self.project['knowledgeModel']['entities'][entity_type][entity_uuid]

    def get_reply(self, question_path: list[str]) -> typing.Optional[dict]:
        return self.project['replies'].get('.'.join(question_path), None)

    def result_add(self, action: str, **kwargs):
        self.result.append({
            'type': action,
            **kwargs,
        })

    def result_debug(self, message: str):
        self.result_add(action='debug', message=message)

    def result_add_item(self, path: str, var_name: str):
        self.result_add(action='addItem', path=path.split('.'), var=var_name)

    def result_set_reply(self, path: str, value: str):
        self.result_add(action='setReply', path=path.split('.'), value=value)

    def result_set_integration_reply(self, path: str, value: str, item_id):
        self.result_add(action='setIntegrationReply', path=path.split('.'), value=value, itemId=item_id)

    def _do_set_variable(self, name: str, value: str):
        self.variables[name] = value

    def _do_j2_variable(self, name: str, template: str):
        self.variables[name] = self.render_jinja2(template)

    def _do_set_item_uuid(self, name: str, item_uuid: str):
        self._do_set_variable(name, item_uuid)

    def _do_add_item(self, template: str, **kwargs):
        rendered = self.render_jinja2(template, **kwargs)
        values = rendered.split('\n', maxsplit=1)
        if len(values) != 2 or len(values[0].strip()) == 0:
            return
        self.result_add_item(
            path=values[0],
            var_name=values[1].strip('\n'),
        )

    def _do_set_reply(self, template: str, **kwargs):
        rendered = self.render_jinja2(template, **kwargs)
        values = rendered.split('\n', maxsplit=1)
        if len(values) != 2 or len(values[0].strip()) == 0:
            return
        self.result_set_reply(
            path=values[0],
            value=values[1].strip('\n'),
        )

    def _do_set_integration_reply(self, template: str, **kwargs):
        rendered = self.render_jinja2(template, **kwargs)
        values = rendered.split('\n', maxsplit=2)
        if len(values) != 3 or len(values[0].strip()) == 0:
            return
        self.result_set_integration_reply(
            path=values[0],
            item_id=values[1].strip('\n'),
            value=values[2].strip('\n'),
        )

    def process_annotations_pre(self, entity: dict, **kwargs):
        for annotation in entity.get('annotations', []):
            key = annotation.get('key', '')  # type: str
            value = annotation.get('value', '')  # type: str
            if key.startswith('fip2dmp.pre.var.set'):
                self._do_set_variable(
                    name=value,
                    value=kwargs.get('_value', ''),
                )
            if key.startswith('fip2dmp.pre.var.set.'):
                self._do_set_variable(
                    name=key[20:],
                    value=value,
                )
            if key.startswith('fip2dmp.var.set'):
                self._do_set_variable(
                    name=value,
                    value=kwargs.get('_value', ''),
                )
            if key.startswith('fip2dmp.var.set.'):
                self._do_set_variable(
                    name=key[16:],
                    value=value,
                )
            if key.startswith('fip2dmp.pre.var.j2.'):
                self._do_set_variable(
                    name=key[19:],
                    value=self.render_jinja2(template=value, **kwargs)
                )
            if key.startswith('fip2dmp.var.j2.'):
                self._do_set_variable(
                    name=key[15:],
                    value=self.render_jinja2(template=value, **kwargs)
                )
            if key == 'fip2dmp.pre.addItem':
                self._do_add_item(template=value, **kwargs)
            if key == 'fip2dmp.pre.setReply':
                self._do_set_reply(template=value, **kwargs)
            if key == 'fip2dmp.pre.setIntegrationReply':
                self._do_set_integration_reply(template=value, **kwargs)

    def process_annotations_post(self, entity: dict, **kwargs):
        for annotation in entity.get('annotations', []):
            key = annotation.get('key', '')  # type: str
            value = annotation.get('value', '')  # type: str
            if key.startswith('fip2dmp.post.var.set'):
                self._do_set_variable(
                    name=value,
                    value=kwargs.get('_value', ''),
                )
            if key.startswith('fip2dmp.post.var.set.'):
                self._do_set_variable(
                    name=key[21:],
                    value=value,
                )
            if key.startswith('fip2dmp.post.var.j2.'):
                self._do_set_variable(
                    name=key[20:],
                    value=self.render_jinja2(template=value, **kwargs)
                )
            if key == 'fip2dmp.addItem' or key == 'fip2dmp.post.addItem':
                self._do_add_item(template=value, **kwargs)
            if key == 'fip2dmp.setReply' or key == 'fip2dmp.post.setReply':
                print(self.variables)
                self._do_set_reply(template=value, **kwargs)
            if key == 'fip2dmp.setIntegrationReply' or key == 'fip2dmp.post.setIntegrationReply':
                self._do_set_integration_reply(template=value, **kwargs)

    def run(self):
        km = self.project['knowledgeModel']
        self.process_annotations_pre(km, _path=[])
        for chapter_uuid in self.project['knowledgeModel']['chapterUuids']:
            self._run_chapter(self.get_entity('chapters', chapter_uuid))
        self.process_annotations_post(km, _path=[])

    def _run_chapter(self, chapter: dict):
        chapter_path = [chapter['uuid']]
        print(f'Chapter: {chapter_path}')
        self.process_annotations_pre(chapter, _path=chapter_path)
        for question_uuid in chapter.get('questionUuids', []):
            self._run_question(
                question=self.get_entity('questions', question_uuid),
                path=chapter_path,
            )
        self.process_annotations_post(chapter, _path=chapter_path)

    def _run_question(self, question: dict, path: list[str]):
        question_path = path + [question['uuid']]
        reply = self.get_reply(question_path)
        if reply is None:
            return
        value = reply['value']['value']

        if question['questionType'] == 'OptionsQuestion':
            answer = self.get_entity('answers', reply['value']['value'])
            if answer is not None:
                self.process_annotations_pre(question, _reply=reply, _path=question_path, _value=value)
                self._run_answer(answer=answer, path=question_path)
                self.process_annotations_post(question, _reply=reply, _path=question_path, _value=value)
        elif question['questionType'] == 'MultiChoiceQuestion':
            self.process_annotations_pre(question, _reply=reply, _path=question_path, _value=value)
            for choice_uuid in reply['value']['value']:
                choice = self.get_entity('choices', choice_uuid)
                if choice is not None:
                    self._run_choice(choice=choice, path=question_path)
            self.process_annotations_post(question, _reply=reply, _path=question_path, _value=value)
        elif question['questionType'] == 'ListQuestion':
            for item_uuid in reply['value']['value']:
                self.process_annotations_pre(question, _reply=reply, _path=question_path, _value=value)
                item_path = question_path + [item_uuid]
                for followup_question_uuid in question.get('itemTemplateQuestionUuids', []):
                    followup_question = self.get_entity('questions', followup_question_uuid)
                    if followup_question is not None:
                        self._run_question(question=followup_question, path=item_path)
                self.process_annotations_post(question, _reply=reply, _path=question_path, _value=value)
        else:
            self.process_annotations_pre(question, _reply=reply, _path=question_path, _value=value)
            self.process_annotations_post(question, _reply=reply, _path=question_path, _value=value)


    def _run_answer(self, answer: dict, path: list[str]):
        answer_path = path + [answer['uuid']]
        self.process_annotations_pre(answer, _path=answer_path)
        for followup_question_uuid in answer.get('', []):
            followup_question = self.get_entity('questions', followup_question_uuid)
            if followup_question is not None:
                self._run_question(question=followup_question, path=answer_path)
        self.process_annotations_post(answer, _path=answer_path)

    def _run_choice(self, choice: dict, path: list[str]):
        choice_path = path + [choice['uuid']]
        self.process_annotations_pre(choice, _path=choice_path)
        self.process_annotations_post(choice, _path=choice_path)


def prepare_import_mapping(project: dict) -> dict:
        executor = _MappingExecutor(project)
        executor.run()
        return {
            'actions': executor.result,
        }
