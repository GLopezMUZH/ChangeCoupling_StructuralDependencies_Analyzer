import logging
from datetime import datetime

import pytz

from .models import ActionClass


def replace_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt


def get_action_class(action_class_name: str) -> ActionClass:
    logging.debug("get_action_class %s", action_class_name)
    if action_class_name in (
        'com.github.gumtreediff.actions.model.Addition',
        'com.github.gumtreediff.actions.model.TreeAddition',
    ):
        return ActionClass.ADD
    if action_class_name in (
        'com.github.gumtreediff.actions.model.Delete',
        'com.github.gumtreediff.actions.model.TreeDelete',
    ):
        return ActionClass.DELETE
    if action_class_name in (
        'com.github.gumtreediff.actions.model.Insert',
        'com.github.gumtreediff.actions.model.TreeInsert',
    ):
        return ActionClass.INSERT
    # TODO from gumtree, get previous parent Function if diff as current...
    if action_class_name in (
        'com.github.gumtreediff.actions.model.Move',
        'com.github.gumtreediff.actions.model.TreeMove',
    ):
        return ActionClass.ADD
    # TODO debug gumtree for update
    if action_class_name in (
        'com.github.gumtreediff.actions.model.Update',
        'com.github.gumtreediff.actions.model.TreeUpdate',
    ):
        return ActionClass.ADD

    raise Exception(f'Unhandled action class name: {action_class_name}')
