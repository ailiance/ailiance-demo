from unittest import mock

from ailiance_demo.services.training_launcher import SSHScreenDispatcher


def test_dispatcher_runs_scp_then_ssh_screen() -> None:
    with mock.patch("subprocess.run") as runner:
        runner.return_value = mock.Mock(returncode=0)
        d = SSHScreenDispatcher(ssh_user="electron")
        d("macm1", "electronics-hw-123", "model: x\n")

    cmds = [tuple(c.args[0][:2]) for c in runner.call_args_list]
    assert ("scp", "-o") in cmds  # write the yaml
    assert ("ssh", "-o") in cmds  # launch screen


def test_dispatcher_raises_on_scp_failure() -> None:
    with mock.patch("subprocess.run") as runner:
        runner.return_value = mock.Mock(returncode=1, stderr=b"permission denied")
        d = SSHScreenDispatcher(ssh_user="electron")
        try:
            d("macm1", "electronics-hw-123", "model: x\n")
        except RuntimeError as exc:
            assert "permission denied" in str(exc)
        else:
            raise AssertionError("expected RuntimeError")
