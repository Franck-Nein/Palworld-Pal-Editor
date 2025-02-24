from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import traceback

from palworld_pal_editor.api.util import reply

from palworld_pal_editor.core import SaveManager, PalEntity
from palworld_pal_editor.utils import LOGGER

pal_blueprint = Blueprint("pal", __name__)

# Update Pal Data
@pal_blueprint.route("/paldata", methods=["PATCH"])
@jwt_required()
def patch_paldata():
    PalGuid = request.json.get("PalGuid")
    PlayerUId = request.json.get("PlayerUId")
    key = request.json.get("key")
    value = request.json.get("value")
    if PlayerUId == "PAL_BASE_WORKER_BTN":
        pal_entity = SaveManager().get_working_pal(PalGuid)
    else:
        pal_entity = SaveManager().get_player(PlayerUId).get_pal(PalGuid)
    try:
        match key:
            case "HasWorkerSick": pal_entity.clear_worker_sick()
            case "IsFaintedPal": pal_entity.heal_pal()
            case "pop_PassiveSkillList": pal_entity.pop_PassiveSkillList(item=value)
            case "pop_MasteredWaza": pal_entity.pop_MasteredWaza(item=value)
            case "pop_EquipWaza": pal_entity.pop_EquipWaza(item=value)
            case "add_PassiveSkillList": 
                if not pal_entity.add_PassiveSkillList(value):
                    return reply(1, None, f"Too many skills, or skill {value} already exists!")
            case "add_MasteredWaza": 
                if not pal_entity.add_MasteredWaza(value):
                    return reply(1, None, f"Too many skills, or skill {value} already exists!")
            case "add_EquipWaza": 
                if not pal_entity.add_EquipWaza(value):
                    return reply(1, None, f"Too many skills, or skill {value} already exists!")
            case _:
                if isinstance(err:=setattr(pal_entity, key, value), TypeError):
                    return reply(1, None, f"Error in patch_paldata {err}")
    except Exception as e:
        stack_trace = traceback.format_exc()
        LOGGER.error(f"Error in patch_paldata {stack_trace}")
        return reply(1, None, f"Error in patch_paldata {stack_trace}")
    return reply(0)

# Get Pal Data
@pal_blueprint.route("/paldata", methods=["POST"])
@jwt_required()
def paldata():
    InstanceId = request.json.get("InstanceId")
    PlayerUId = request.json.get("PlayerUId")
    if PlayerUId == "PAL_BASE_WORKER_BTN":
        pal = SaveManager().get_working_pal(InstanceId)
        LOGGER.info(f"Get BASE WORKER {pal}")
    else:
        try:
            player = SaveManager().get_player(PlayerUId)
            pal = player.get_pal(InstanceId)
            LOGGER.info(f"Get {player.NickName}'s pal: {pal}")
        except:
            pass
    if pal:
        return reply(
            0,
            _pal_data(pal),
        )
    LOGGER.warning(
        f"Failed Getting Pal with PlayerID: {PlayerUId}, PalID: {InstanceId}"
    )
    return reply(
        1, f"Failed Getting Pal with PlayerID: {PlayerUId}, PalID: {InstanceId}"
    )

# Just some dumb shit
def _pal_data(pal: PalEntity):
    return {
        "InstanceId": str(pal.InstanceId) if pal.InstanceId else None,
        "OwnerPlayerUId": (str(pal.OwnerPlayerUId) if pal.OwnerPlayerUId else None),
        "OwnerName": pal.OwnerName or None,
        "IconAccessKey": pal.IconAccessKey or None,
        "DataAccessKey": pal.DataAccessKey or None,
        "I18nName": pal.I18nName or None,
        "DisplayName": pal.DisplayName or None,
        "HasTowerVariant": pal.HasTowerVariant,
        "IsPal": pal.IsPal,
        "IsHuman": pal.IsHuman,
        "Gender": pal.Gender.value if pal.Gender else None,
        "IsTower": pal.IsTower or False,
        "IsBOSS": pal.IsBOSS or False,
        "IsRarePal": pal.IsRarePal or False,
        "NickName": pal.NickName or "",
        "Level": pal.Level or 1,
        "Rank": pal.Rank.value if pal.Rank else 1,
        "Rank_HP": pal.Rank_HP or 0,
        "Rank_Attack": pal.Rank_Attack or 0,
        "Rank_Defence": pal.Rank_Defence or 0,
        "Rank_CraftSpeed": pal.Rank_CraftSpeed or 0,
        "MaxHP": pal.MaxHP or None,
        "ComputedAttack": pal.ComputedAttack or None,
        "ComputedDefense": pal.ComputedDefense or None,
        "ComputedCraftSpeed": pal.ComputedCraftSpeed or None,
        "PassiveSkillList": pal.PassiveSkillList or [],
        "EquipWaza": pal.EquipWaza or [],
        "MasteredWaza": pal.MasteredWaza or [],
        "Talent_HP": pal.Talent_HP or 0,
        "Talent_Melee": pal.Talent_Melee or 0,
        "Talent_Shot": pal.Talent_Shot or 0,
        "Talent_Defense": pal.Talent_Defense or 0,
        "HasWorkerSick": pal.HasWorkerSick,
        "IsFaintedPal":pal.IsFaintedPal,
        "group_id": str(pal.group_id) if pal.group_id else None,
        "ContainerId": str(pal.ContainerId) if pal.CharacterID else None,
        "SlotIndex": pal.SlotIndex
    }

@pal_blueprint.route("/dump_data", methods=["POST"])
@jwt_required()
def dump_data():
    PalGuid = request.json.get("PalGuid")
    PlayerUId = request.json.get("PlayerUId")
    if PlayerUId == "PAL_BASE_WORKER_BTN":
        pal = SaveManager().get_working_pal(PalGuid)
        LOGGER.info(f"Get BASE WORKER {pal}")
    else:
        try:
            player = SaveManager().get_player(PlayerUId)
            pal = player.get_pal(PalGuid)
            LOGGER.info(f"Get {player.NickName}'s pal: {pal}")
        except:
            pass
    if pal:
        return reply(0, pal.dump_obj())
    LOGGER.warning(f"Failed Getting Pal with PlayerID: {PlayerUId}, PalID: {PalGuid}")
    return reply(1, f"Failed Getting Pal with PlayerID: {PlayerUId}, PalID: {PalGuid}")