import copy
from datetime import datetime
from pathlib import Path
import shutil
from typing import Optional

from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.archive import FArchiveReader, FArchiveWriter, UUID
from palworld_save_tools.json_tools import CustomEncoder
from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

from palworld_pal_editor.core.pal_objects import UUID2HexStr, get_attr_value, toUUID
from palworld_pal_editor.core.player_entity import PlayerEntity
from palworld_pal_editor.core.pal_entity import PalEntity
from palworld_pal_editor.utils import LOGGER, alphanumeric_key


def skip_decode(reader: FArchiveReader, type_name: str, size: int, path: str):
    if type_name == "ArrayProperty":
        array_type = reader.fstring()
        value = {
            "skip_type": type_name,
            "array_type": array_type,
            "id": reader.optional_guid(),
            "value": reader.read(size),
        }
    elif type_name == "MapProperty":
        key_type = reader.fstring()
        value_type = reader.fstring()
        _id = reader.optional_guid()
        value = {
            "skip_type": type_name,
            "key_type": key_type,
            "value_type": value_type,
            "id": _id,
            "value": reader.read(size),
        }
    elif type_name == "StructProperty":
        value = {
            "skip_type": type_name,
            "struct_type": reader.fstring(),
            "struct_id": reader.guid(),
            "id": reader.optional_guid(),
            "value": reader.read(size),
        }
    else:
        raise Exception(
            f"Expected ArrayProperty or MapProperty or StructProperty, got {type_name} in {path}"
        )
    return value


def skip_encode(writer: FArchiveWriter, property_type: str, properties: dict) -> int:
    if "skip_type" not in properties:
        if properties["custom_type"] in PALWORLD_CUSTOM_PROPERTIES is not None:
            return PALWORLD_CUSTOM_PROPERTIES[properties["custom_type"]][1](
                writer, property_type, properties
            )
        else:
            # Never be run to here
            return writer.property_inner(writer, property_type, properties)
    if property_type == "ArrayProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["array_type"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    elif property_type == "MapProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["key_type"])
        writer.fstring(properties["value_type"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    elif property_type == "StructProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["struct_type"])
        writer.guid(properties["struct_id"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    else:
        raise Exception(
            f"Expected ArrayProperty or MapProperty or StructProperty, got {property_type}"
        )


MAIN_SKIP_PROPERTIES = copy.deepcopy(PALWORLD_CUSTOM_PROPERTIES)
MAIN_SKIP_PROPERTIES[".worldSaveData.MapObjectSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.FoliageGridSaveDataMap"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.MapObjectSpawnerInStageSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.DynamicItemSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.ItemContainerSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.WorkSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.DungeonSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.EnemyCampSaveData"] = (skip_decode, skip_encode)

MAIN_SKIP_PROPERTIES[".worldSaveData.InvaderSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.DungeonPointMarkerSaveData"] = (skip_decode, skip_encode)
MAIN_SKIP_PROPERTIES[".worldSaveData.GameTimeSaveData"] = (skip_decode, skip_encode)

# PALEDITOR_CUSTOM_PROPERTIES[".worldSaveData.CharacterContainerSaveData"] = (skip_decode, skip_encode)
# PALEDITOR_CUSTOM_PROPERTIES[".worldSaveData.GroupSaveDataMap"] = (skip_decode, skip_encode)


PLAYER_SKIP_PROPERTIES = copy.deepcopy(PALWORLD_CUSTOM_PROPERTIES)
PLAYER_SKIP_PROPERTIES[".SaveData.PlayerCharacterMakeData"] = (skip_decode, skip_encode)
PLAYER_SKIP_PROPERTIES[".SaveData.LastTransform"] = (skip_decode, skip_encode)
PLAYER_SKIP_PROPERTIES[".SaveData.inventoryInfo"] = (skip_decode, skip_encode)
PLAYER_SKIP_PROPERTIES[".SaveData.RecordData"] = (skip_decode, skip_encode)

class SaveManager:
    # Although these are class attrs, SaveManager itself is singleton.
    _instance = None
    _file_path: Optional[Path]
    _raw_gvas: Optional[bytes]
    _compression_times: Optional[int]

    gvas_file: Optional[GvasFile]
    entities_list: Optional[list[dict]]
    player_mapping: Optional[dict[str, PlayerEntity]]
    baseworker_mapping: Optional[dict[str, PalEntity]]
    _dangling_pals: Optional[dict[str, PalEntity]]
    

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True

    def get_players(self) -> list[PlayerEntity]:
        return self.player_mapping.values()
    
    def get_player(self, guid: UUID | str) -> Optional[PlayerEntity]:
        if guid is None: return
        # TODO Use str instead of UUID
        # actually uuid and str works the same because both eq and hash using str
        guid = str(guid)
        if guid in self.player_mapping:
            player = self.player_mapping[guid]
            return player
        LOGGER.warning(f"Player {guid} not exist")

    def get_players_by_name(self, name: str) -> list[PlayerEntity]:
        return [player for player in self.get_players() if player.NickName == name]
    
    def get_working_pal(self, guid: UUID | str) -> Optional[PalEntity]:
        return self.baseworker_mapping.get(str(guid), None)

    def get_pal(self, guid: UUID | str) -> Optional[PalEntity]:
        for player in self.get_players():
            if pal := player.get_pal(guid):
                return pal
        if guid in self.baseworker_mapping:
            return self.baseworker_mapping[guid]
        if guid in self._dangling_pals:
            return self._dangling_pals[guid]
        LOGGER.warning(f"Can't find pal {guid}")

    def get_working_pals(self) -> list[PalEntity]:
        return sorted(self.baseworker_mapping.values(), key=lambda pal: (alphanumeric_key(pal.PalDeckID), pal.Level or 1))

    def _load_entities(self):
        self.player_mapping = {}
        self._dangling_pals = {}
        self.baseworker_mapping = {}
        temp_player_pal_mapping: dict[str, dict[str, PalEntity]] = {}
        for entity in self.entities_list:
            entity_struct = entity["value"]["RawData"]["value"]["object"]["SaveParameter"]
            if entity_struct['struct_type'] != 'PalIndividualCharacterSaveParameter':
                LOGGER.warning(f"Non-player/pal data found in CharacterSaveParameterMap, skipping {entity}")
                continue

            entity_param = entity_struct['value']
            try: 
                if get_attr_value(entity_param, "IsPlayer"):
                    uid_str = str(get_attr_value(entity['key'], "PlayerUId"))

                    if uid_str in self.player_mapping:
                        LOGGER.error(f"Duplicated player found: \n\t{self.player_mapping[uid_str]}, skipping...")
                        continue

                    player_gvas_file, player_compress_times = self.load_player_sav(uid_str)

                    if uid_str in temp_player_pal_mapping:
                        player_entity = PlayerEntity(entity, temp_player_pal_mapping[uid_str], player_gvas_file, player_compress_times)
                        del temp_player_pal_mapping[uid_str]
                    else:
                        player_entity = PlayerEntity(entity, dict(), player_gvas_file, player_compress_times)
                
                    self.player_mapping[uid_str] = player_entity
                    LOGGER.info(f"Found player: {player_entity}")
                else:
                    pal_entity = PalEntity(entity)
                    owner = pal_entity.OwnerPlayerUId
                    if owner:
                        owner_str = str(owner)
                        if owner_str in self.player_mapping:
                            self.player_mapping[owner_str].add_pal(pal_entity)
                        else:
                            temp_player_pal_mapping.setdefault(owner_str, dict())[str(pal_entity.InstanceId)] = pal_entity
                        LOGGER.info(f"Found pal: {pal_entity}")

                    else:
                        if pal_entity.OldOwnerPlayerUIds:
                            self.baseworker_mapping[str(pal_entity.InstanceId)] = pal_entity
                            continue
                        self._dangling_pals[str(pal_entity.InstanceId)] = pal_entity
                        LOGGER.error(f"Found dangling pal object: {pal_entity}, skipping")
                        continue

            except Exception as e:
                LOGGER.error(f"Error occured while init'in object: {e}, skipping")
                continue

        
        for player in self.player_mapping.values():
            LOGGER.newline()
            LOGGER.info(f"{player}")
            sorted_palbox = player.get_sorted_pals()
            for pal in sorted_palbox:
                LOGGER.info(f"\t{pal}")
        
        LOGGER.newline()
        LOGGER.info("Pals possibly working at the base: ")
        for pal in self.get_working_pals():
            LOGGER.info(f"\t{pal}")

        LOGGER.newline()
        LOGGER.info("Dangling Pals (No OwnerID and OldOwnerID): ")
        for pal in self._dangling_pals.values():
            LOGGER.warning(f"\t{pal}")

        for uid_str in temp_player_pal_mapping:
            pal_list = temp_player_pal_mapping[uid_str]
            LOGGER.newline()
            LOGGER.warning(f"Found dangling pals owned by non-existing user {uid_str}")
            for pal in pal_list.values():
                self._dangling_pals[str(pal.InstanceId)] = pal
                LOGGER.warning(f"\t{pal}")
                
    def open(self, file_path: str) -> Optional[GvasFile]:
        self._file_path = Path(file_path).resolve()

        level_sav_path = self._file_path / "Level.sav"

        if not level_sav_path.exists():
            LOGGER.error(f"Save file does not exist: {level_sav_path}.")
            return None

        LOGGER.info(f"Opening {level_sav_path}")
        with level_sav_path.open("rb") as file:
            data = file.read()

            try:
                LOGGER.info("Decompressing sav")
                self._raw_gvas, self._compression_times = decompress_sav_to_gvas(data)
            except Exception as e:
                LOGGER.error(f"Caught Exception: palworld_save_tools::palsav::decompress_sav_to_gvas: {e}")
                return None

            LOGGER.info("Reading GVAS file")
            self.gvas_file = GvasFile.read(
                self._raw_gvas, PALWORLD_TYPE_HINTS, MAIN_SKIP_PROPERTIES
            )

            try:
                self.entities_list = self.gvas_file.properties["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"]
            except Exception as e:
                LOGGER.error(f"Unable to retrieve pal data: {e}")
                return None

            self._load_entities()

            LOGGER.info("Done")
        return self.gvas_file

    def save(self, file_path: str) -> bool:
        if self.gvas_file is None:
            LOGGER.error("No gvas_file stored in save manager, aborting")
            return False
        if self._compression_times is None:
            LOGGER.warning("_compression_times is None, aborting")
            return False

        output_path = Path(file_path).resolve() 

        if not output_path.exists():
            LOGGER.error(f"Path does not exist: {output_path}")
            if output_path.parent.exists():
                output_path.mkdir(parents=True, exist_ok=True)
                LOGGER.debug(f"Path {output_path} created")
            else:
                LOGGER.error(f"Parent path {output_path.parent} does not exist, skipping")
                return False
            
        file_path: Path = output_path / "Level.sav"

        if file_path.exists():
            BK_FOLDER_NAME = "Palworld-Pal-Editor-Backup"
            backup_dir = output_path / BK_FOLDER_NAME / f"{output_path.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                if output_path.exists():
                    LOGGER.info(f"Backing up {output_path} to {backup_dir}")
                    shutil.copytree(output_path, backup_dir, 
                                    ignore=lambda dir, files: [f for f in files if not f == "Players" and not f.endswith('.sav')])
                else:
                    LOGGER.info(f"No existing directory to backup: {output_path}")
            except Exception as e:
                LOGGER.error(f"Error backing up directory: {e}")
                return False

        LOGGER.info("Saving Player Data...")
        for player in self.player_mapping.values():
            self.save_player_sav(player)

        LOGGER.info("Saving Level.sav...")
        gvas_file = copy.deepcopy(self.gvas_file)
        LOGGER.info("Compressing Main GVAS file")
        sav_data = compress_gvas_to_sav(
            gvas_file.write(MAIN_SKIP_PROPERTIES), self._compression_times
        )

        LOGGER.info(f"Saving to {file_path}")
        with file_path.open("wb") as file:
            file.write(sav_data)
        LOGGER.info(f"Saved to {file_path}")
        return True
    
    def load_player_sav(self, player_uid: str | UUID) -> GvasFile:
        player_path: Path = self._file_path / "Players" / f"{UUID2HexStr(player_uid)}.sav"
        LOGGER.info(f"Loading Player SAV: {player_path}")
        if not player_path.exists():
            LOGGER.error(f"Player SAV {str(player_path.absolute())} not exist")
            raise Exception(f"Player SAV {str(player_path.absolute())} not exist")
        with player_path.open("rb") as player_file:
            player_data = player_file.read()
        raw_gvas, compression_times = decompress_sav_to_gvas(player_data)
        player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PLAYER_SKIP_PROPERTIES)
        return player_gvas_file, compression_times
    
    
    def save_player_sav(self, player_entity: PlayerEntity) -> bool:
        if player_entity.PlayerGVAS is None:
            return False

        gvas_file, compression_times = player_entity.PlayerGVAS
        player_path: Path = self._file_path / "Players" / f"{UUID2HexStr(player_entity.PlayerUId)}.sav"

        LOGGER.info(f"Compressing Player {player_entity} GVAS file")
        player_gvas_file = copy.deepcopy(gvas_file)
        sav_data = compress_gvas_to_sav(
            player_gvas_file.write(PLAYER_SKIP_PROPERTIES), compression_times
        )

        LOGGER.info(f"Saving to {player_path}")
        with player_path.open("wb") as file:
            file.write(sav_data)
        LOGGER.info(f"Saved to {player_path}")
        return True
