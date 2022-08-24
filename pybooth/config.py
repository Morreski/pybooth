import os
import argparse
import dataclasses
import configparser
import warnings


@dataclasses.dataclass
class Config:
    output_dir: str
    compositions_folder_name: str
    original_captures_folder_name: str

    composition_yaml_path: str
    composition_test_mode: bool
    events_log_path: str

    camera_type: str

    webserver_enabled: bool
    webserver_port: int

    @staticmethod
    def get_composition_section_from_ini_config(cfg: configparser.ConfigParser):
        compositions_sections = [
            s for s in cfg.sections() if s.startswith("Composition.")
        ]
        composition = None
        if len(compositions_sections) > 0:
            composition = compositions_sections[0]
            if len(compositions_sections) > 1:
                warnings.warn("Multiple compositions are not supported. ...yet !")
        return composition

    @classmethod
    def from_program_args(cls):
        """Load from program args (and ini file if specified in program args)
        Note that program arguments have higher precedence than value in config file if both are supplied
        """
        args = _parse_program_args()
        cfg = configparser.ConfigParser()
        if args.config:
            cfg.read(args.config)

        composition = cls.get_composition_section_from_ini_config(cfg)

        return cls(
            output_dir=args.dest or cfg.get("Output", "base_dir", fallback="./booth"),
            compositions_folder_name=cfg.get(
                "Output", "original_captures_folder_name", fallback="compositions"
            ),
            original_captures_folder_name=cfg.get(
                "Output", "compositions_folder_name", fallback="pictures"
            ),
            composition_yaml_path=args.composition
            or cfg.get(composition, "yaml_path", fallback="")
            or None,
            composition_test_mode=args.debug
            or cfg.getboolean("General", "debug", fallback=False),
            camera_type=args.camera_type
            or cfg.get("Camera", "engine", fallback="gphoto"),
            events_log_path=args.events_log_path
            or cfg.get("Events", "log_path", fallback="/tmp/booth_events.log"),
            webserver_enabled=args.web is not None
            or cfg.getboolean("Webserver", "enabled", fallback=False),
            webserver_port=args.web or cfg.getint("Webserver", "port", fallback=1502),
        )

    @property
    def compositions_dest_dir(self):
        return os.path.join(self.output_dir, self.compositions_folder_name)

    @property
    def captures_dest_dir(self):
        return os.path.join(self.output_dir, self.original_captures_folder_name)


def _parse_program_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--composition",
        metavar="FILE",
        help="Image used as background for composition",
    )
    parser.add_argument(
        "--config",
        "-c",
        metavar="INI_FILE",
        help="Path to config file",
    )
    parser.add_argument(
        "--dest",
        "-d",
        metavar="PATH",
        help="Root folder of photbooth media outputs",
    )
    parser.add_argument(
        "--camera_type",
        metavar="VALUE",
        choices=("gphoto", "dummy"),
        help="Camera backend to use",
    )
    parser.add_argument(
        "--events_log_path",
        "-e",
        metavar="PATH",
        help="Append only event log path",
    )
    parser.add_argument(
        "--web",
        metavar="PORT",
        type=int,
        help="Start webserver on specified port",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: will show compositions after rendering and will not save them on disk",
    )
    return parser.parse_args()
