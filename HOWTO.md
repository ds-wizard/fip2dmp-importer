# How to Specify KM Mapping

To allow this importer to import replies to a questionnaire with a certain (target) KM, the mapping from source KM must be specified. It can be done using KM annotations in the source KM. To do the mapping, one must know UUIDs (more specifically UUID paths for desired replies) from the target KM. Then, the annotations can be used to simply specify what reply should be placed to which path. 

## Knowledge Model Annotations

The annotations can be placed to any entity in KM; however, this importer takes into account only those specified on: 

- *knowledge model* = used exactly once for entire questionnaire,
- *chapter* = used when entering/leaving the chapter during traversal,
- *question* = used when question has a reply,
- *answer* or *choice* = used when it is selected.

There are the following possible annotations to be used in these entities:

### `fip2dmp.var.set`

Should be used only for question, it stores value of the reply in the variable named in the value. For example, if this annotation is used on a value question and the annotation has value `personName`; it will set variable `personName` with the value of the question reply in its contents.

Variants:

* `fip2dmp.pre.var.set` (default) = processing before traversing deeper in KM
* `fip2dmp.post.var.set` = processing after traversing deeper in KM

### `fip2dmp.var.set.<name>`

Similarly to the previous one, it creates a variable; however, the name must be given in the key and then the value is the value of the variable. This can be used to specify some constants or eventually to clear some already defined variables.

Variants:

* `fip2dmp.pre.var.set.<name>` (default) = processing before traversing deeper in KM
* `fip2dmp.post.var.set.<name>` = processing after traversing deeper in KM

### `fip2dmp.var.j2.<name>`

Just as the previous one, except the value can be a [Jinja2] template using other variables set and the global variables described below. Name must be given in the annotation key. For example, you could use it to process a reply value from options question:

```j2
{%- if _value == "..." -%}
The value is correctly selected and ...
{%- else -%}
N/A
{%- endif -%}
```

Variants:

* `fip2dmp.pre.var.j2.<name>` (default) = processing before traversing deeper in KM
* `fip2dmp.post.var.j2.<name>` = processing after traversing deeper in KM

### `fip2dmp.addItem`

This annotation can be used to add an item in the target questionnaire for a certain list question. The value of the annotation is entirely a [Jinja2] template where on the first line must be the reply path in the target questionnaire and then on the second line is variable name for storing the item UUID (to be used in paths).

```j2
3a435143-4ae5-4aae-9de5-48eaf921fec0.34f04d1c-81a9-4300-9699-add5f2115258
personItemUuid
```

The `personItemUuid` is the variable name; however, the actual UUID is not known prior to the import. Thus, you must use this variable as is and not as Jinja2 variable (see the example in the following section).

Variants:

* `fip2dmp.pre.addItem` = processing before traversing deeper in KM
* `fip2dmp.post.addItem` (default) = processing after traversing deeper in KM

### `fip2dmp.setReply`

This annotation can be used to set a reply in the target questionnaire. The value of the annotation is entirely a [Jinja2] template where on the first line must be the reply path in the target questionnaire and then from the second line is the actual reply:

```j2
3a435143-4ae5-4aae-9de5-48eaf921fec0.34f04d1c-81a9-4300-9699-add5f2115258.personItemUuid.ca51881d-a0b2-4753-a96b-6dfaad7a28f2
This is {{ someVar }} imported to the target path...
```

You can of course store UUIDs in Jinja2 variables, e.g. using the `fip2dmp.var.set.<name>` annotation, and then use it like this:

```j2
{{ infoChapterUuid }}.{{ authorsQuestionUuid }}.personItemUuid.{{ descriptionQuestionUuid }}
This is {{ someVar }} imported to the target path...
```

Variants:

* `fip2dmp.pre.setReply` = processing before traversing deeper in KM
* `fip2dmp.post.setReply` (default) = processing after traversing deeper in KM

### `fip2dmp.setIntegrationReply`

This annotation work similarly to the previous one, but it is intended for integration questions where you want to also set the *item ID* (typically URI or its part):

```j2
{{ infoChapterUuid }}.{{ authorsQuestionUuid }}.personItemUuid.{{ affiliationQuestionUuid }}
https://example.com/org/{{ organizationId }}
**{{ organizationName }}**
{% if organizationDescription|length > 0 %}
{{ organizationDescription }}
{% else %}
*No description provided*
{% endif %}
```

Variants:

* `fip2dmp.pre.setIntegrationReply` = processing before traversing deeper in KM
* `fip2dmp.post.setIntegrationReply` (default) = processing after traversing deeper in KM

## Available Predefined Variables

It is possible to use the following variables in all Jinja2 fragments (should not be overriden):

* `_ctx` = complete context of the source questionnaire that contains also the compiled source `knowledgeModel`.
* `_result` = list of instructions for importing replies, each object have `action` field and then other based on it; it can be used for debugging purposes and manually adding actions if necessary.
* `_value` = (only on questions) value of the reply.
* `_reply` = (only on questions) reply object.
* `_path` = current path as a list of UUIDs.

## Traversal and Mapping

The source KM is traversed in-order, first processing `pre` annotations, then following deeper entities (e.g. from chapter to questions) and then processing `post` annotations. During the traversal, variables are updated and commands added to the `_result` variable which is then used for the actual import to the target questionnaire.

On list question, the annotations are processed before/after each item (i.e. sub-questionnaire). That is mainly useful for the `addItem` annotation.

All the variables set using annotations during the traversal are available to all [Jinja2] templates. But variables specified inside a template via `{%- set foo = "bar" -%}` are only local to the template.


[Jinja2]: https://jinja.palletsprojects.com/en/
