#coding=utf-8
"""Test pulpcore features using multiple plugins."""
import unittest

from pulp_smash import api, cli, config
from pulp_smash.pulp3.constants import MEDIA_PATH, REPO_PATH
from pulp_smash.pulp3.utils import (
    gen_repo,
    gen_remote,
    get_added_content,
    get_content,
    sync,
)

from pulpcore.tests.functional.api.using_plugin.constants import (
    FILE_FIXTURE_MANIFEST_URL,
    FILE_REMOTE_PATH,
    RPM_REMOTE_PATH,
    RPM_UNSIGNED_FIXTURE_URL,
)


class SyncManyPluginsTestCase(unittest.TestCase):
    """Sync a repository using differnt remotes with different plugins.
    
    This test targets the following issue:

    https://pulp.plan.io/issues/4274
    
    """
    def test_all(self):
        """Sync a repository using different remotes with different plugins."""
        cfg = config.get_config()
        client = api.Client(cfg, api.page_handler)

        rpm_remote = client.post(
            RPM_REMOTE_PATH,
            gen_remote(RPM_UNSIGNED_FIXTURE_URL)
        )
        self.addCleanup(client.delete, rpm_remote['_href'])

        file_remote = client.post(
            FILE_REMOTE_PATH,
            gen_remote(FILE_FIXTURE_MANIFEST_URL)
        )
        self.addCleanup(client.delete, file_remote['_href'])
        
        repo = client.post(REPO_PATH, gen_repo())
        self.addCleanup(client.delete, repo['_href'])

        # first sync
        sync(cfg, file_remote, repo)
        repo = client.get(repo['_href'])

        # from pprint import pprint
        # from ipdb import set_trace
        # set_trace()

        # second sync
        sync(cfg, rpm_remote, repo)


http POST http://localhost:80/pulp/api/v3/repositories/ name=foo
export REPO_HREF=$(http localhost:80/pulp/api/v3/repositories/ | jq -r '.results[] | select(.name == "foo") | ._href')
http POST http://localhost:80/pulp/api/v3/remotes/file/file/ name='bar' url='https://repos.fedorapeople.org/pulp/pulp/demo_repos/test_file_repo/PULP_MANIFEST'
export FILE_REMOTE_HREF=$(http localhost:80/pulp/api/v3/remotes/file/file | jq -r '.results[] | select(.name == "bar") | ._href')
http POST http://localhost:80'$FILE_REMOTE_HREF'sync/ repository=$REPO_HREF mirror=True

http POST http://localhost:8000/pulp/api/v3/remotes/rpm/rpm/ name='bar' url='https://repos.fedorapeople.org/pulp/pulp/fixtures/rpm-unsigned/'
export RPM_REMOTE_HREF=$(http :8000/pulp/api/v3/remotes/rpm/rpm/ | jq -r '.results[] | select(.name == "bar") | ._href')
http POST :8000${RPM_REMOTE_HREF}sync/ repository=$REPO_HREF