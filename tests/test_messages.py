from damnsshmanager.messages import Messages


def test_init():
    try:
        Messages()
    except IOError:
        assert False


def test_valid_message():
    m = Messages()
    assert m.get('add.help') == ('Add new host alias by'
                                 ' providing alias and host names')


def test_missing_section():
    m = Messages()
    assert m.get('missing', section='MISSING') is None


def test_missing_message():
    m = Messages()
    assert m.get('missing') is None
