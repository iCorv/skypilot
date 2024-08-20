import pathlib
from typing import Dict
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from sky import clouds
from sky import skypilot_config
from sky.backends import backend_utils
from sky.resources import Resources
from sky.resources import resources_utils


@patch.object(skypilot_config, "CONFIG_PATH", "./tests/test_yamls/test_aws_config.yaml")
@patch.object(skypilot_config, "_dict", None)
@patch.object(skypilot_config, "_loaded_config_path", None)
@patch("sky.clouds.service_catalog.instance_type_exists", return_value=True)
@patch(
    "sky.clouds.service_catalog.get_accelerators_from_instance_type",
    return_value={"fake-acc": 2},
)
@patch("sky.clouds.service_catalog.get_image_id_from_tag", return_value="fake-image")
@patch.object(clouds.aws, "DEFAULT_SECURITY_GROUP_NAME", "fake-default-sg")
@patch("sky.check.get_cloud_credential_file_mounts", return_value="~/.aws/credentials")
@patch(
    "sky.backends.backend_utils._get_yaml_path_from_cluster_name",
    return_value="/tmp/fake/path",
)
@patch("sky.utils.common_utils.fill_template")
def test_write_cluster_config_w_remote_identity(mock_fill_template, *mocks) -> None:
    skypilot_config._try_load_config()

    cloud = clouds.AWS()

    region = clouds.Region(name="us-west-2")
    zones = [clouds.Zone(name="b")]
    resource = Resources(cloud=cloud, instance_type="p4d.24xlarge")

    cluster_config_template = "aws-ray.yml.j2"

    print(skypilot_config._dict)

    # test default
    config = backend_utils.write_cluster_config(
        to_provision=resource,
        num_nodes=2,
        cluster_config_template=cluster_config_template,
        cluster_name="display",
        local_wheel_path=pathlib.Path("/tmp/fake"),
        wheel_hash="b1bd84059bc0342f7843fcbe04ab563e",
        region=region,
        zones=zones,
        dryrun=False,
        keep_launch_fields_in_existing_config=True,
    )
    import os

    # copy the generated config from the temp directory to the current directory
    os.system(f"cp {config['ray']} .")
