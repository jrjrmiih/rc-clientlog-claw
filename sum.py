import ckey


class Sum:
    def __init__(self):
        self.navi = {ckey.REQ: 0, ckey.REP: 0, ckey.SUCCESS: 0, ckey.FAILED: 0, ckey.ERRCODE: {}}
        # handled platver.
        self.hpv = {}
        # unhandled platver.
        self.uhpv = {}

    def summary(self):
        sumdict = {ckey.HPV: self.hpv, ckey.UHPV: self.uhpv, ckey.NAVI: self.navi}
        return sumdict.__str__()

    def flush(self, entity):
        # flush handled or unhandled platver.
        if entity.abs[ckey.SUPPORT]:
            self.hpv[entity.abs[ckey.PLATVER]] = \
                1 if entity.abs[ckey.PLATVER] not in self.hpv else self.hpv[entity.abs[ckey.PLATVER]] + 1
        else:
            self.uhpv[entity.abs[ckey.PLATVER]] = \
                1 if entity.abs[ckey.PLATVER] not in self.uhpv else self.uhpv[entity.abs[ckey.PLATVER]] + 1

        # flush navi.
        self.navi[ckey.REQ] = self.navi[ckey.REQ] + entity.navi[ckey.REQ]
        self.navi[ckey.REP] = self.navi[ckey.REP] + entity.navi[ckey.REP]
        self.navi[ckey.SUCCESS] = self.navi[ckey.SUCCESS] + entity.navi[ckey.SUCCESS]
        self.navi[ckey.FAILED] = self.navi[ckey.FAILED] + entity.navi[ckey.FAILED]
        for key, value in entity.navi[ckey.ERRCODE].items():
            self.navi[ckey.ERRCODE][key] = \
                value if key not in self.navi[ckey.ERRCODE] else self.navi[ckey.ERRCODE][key] + value
