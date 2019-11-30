#!/usr/bin/python3


def test_permissions(share, options):
    assert share.isPermittedModule(options, share.mint.signature)


def hooks(options):
    result = options.getPermissions()
    assert result["hooks"] == ("0x741b5078",)
    assert result["hookBools"] == 2 ** 256 - 1
