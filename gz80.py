from interface import *
from functions import *

regs = ["b", "c", "d", "e", "h", "l", Memory8("hl"), "a"]
regpairs = ["bc", "de", "hl", "sp"] 

x0z2 = [Instruction("ld (bc),a", {Memory8("bc"): "a", "pc": [add, "pc", 1]}),
        Instruction("ld a,(bc)", {"a": Memory8("bc"), "pc": [add, "pc", 1]}),
        Instruction("ld (de),a", {Memory8("de"): "a", "pc": [add, "pc", 1]}),
        Instruction("ld a,(de)", {"a": Memory8("de"), "pc": [add, "pc", 1]}),
        Instruction("ld (hl+),a", {Memory8("hl"): "a", "hl": [add, "hl", 1], "pc": [add, "pc", 1]}),
        Instruction("ld a,(hl+)", {"a": Memory8("hl"), "hl": [add, "hl", 1], "pc": [add, "pc", 1]}),
        Instruction("ld (hl-),a", {Memory8("hl"): "a", "hl": [sub, "hl", 1], "pc": [add, "pc", 1]}),
        Instruction("ld a,(hl-)", {"a": Memory8("hl"), "hl": [sub, "hl", 1], "pc": [add, "pc", 1]})]

x0z7 = [Instruction("rlca", 
            {"a": [rotleft, 1, 8, "a"], 
             "pc": [add, "pc", 1],
             "z": 0, "n": 0, "h": 0, "c": [bit, 7, "a"]}),
        Instruction("rrca", 
            {"a": [rotright, 1, 8, "a"],
             "pc": [add, "pc", 1],
             "z": 0, "n": 0, "h": 0, "c": [bit, 0, "a"]}),
        Instruction("rla", 
            {"a": [orl, [shiftleft, 1, "a"], [shiftleft, 7, "c"]],
             "pc": [add, "pc", 1],
             "z": 0, "n": 0, "h": 0, "c": [bit, 7, "a"]}),
        Instruction("rra", 
            {"a": [orl, [shiftright, 1, "a"], [shiftleft, 7, "c"]],
             "pc": [add, "pc", 1],
             "z": 0, "n": 0, "h": 0, "c": [bit, 0, "a"]}),
        Instruction("daa", #This instruction is going to give me nightmares
            {"a": [if_, [orl, "h", [gt, [xorl, "a", 0xf], 0x9]],
                    [if_, [orl, [gt, [xorl, [add, "a", 0x06], 0xf0], 0x90], "c"],
                        [add, "a", 0x66],
                        [add, "a", 0x06]],
                    [if_, [orl, [gt, [xorl, "a", 0xf0], 0x90], "c"],
                        [add, "a", 0x60],
                        "a"]], # Maybe this should be optimised later to get rid of the if statements
             "c": [orl, [gt, [xorl, [add, "a", [mul, 0x06, [orl, "h", [gt, [xorl, "a", 0xf], 0x9]]]], 0xf0], 0x90], "c"],
             "h": 0,
             "z": [eq, [if_, [orl, "h", [gt, [xorl, "a", 0xf], 0x9]],
                    [if_, [orl, [gt, [xorl, [add, "a", 0x06], 0xf0], 0x90], "c"],
                        [add, "a", 0x66],
                        [add, "a", 0x06]],
                    [if_, [orl, [gt, [xorl, "a", 0xf0], 0x90], "c"],
                        [add, "a", 0x60],
                        "a"]], 0],
             "pc": [add, "pc", 1]}), # end of daa
        Instruction("cpl", 
            {"a": [xorl, "a", 0xff],
             "pc": [add, "pc", 1],
             "n": 1, "h": 1}),
        Instruction("scf", 
            {"pc": [add, "pc", 1],
             "n": 0, "h": 0, "c": 1}),
        Instruction("ccf", 
            {"pc": [add, "pc", 1],
             "n": 0, "h": 0, "c": 0})]

class gz80(Processor):
    def getDescription(self):
        return { "pc" : ProgramCounter(16),
                 "af" : Register(16),
                 "bc" : Register(16),
                 "de" : Register(16),
                 "hl" : Register(16),
                 "sp" : Register(16),
                 "a"  : SubRegister("af", 8, 7),
                 "b"  : SubRegister("bc", 8, 7),
                 "c"  : SubRegister("bc", 8, 0),
                 "d"  : SubRegister("de", 8, 7),
                 "e"  : SubRegister("de", 8, 0),
                 "h"  : SubRegister("hl", 8, 7),
                 "l"  : SubRegister("hl", 8, 0),
                 # cpu state
                 "interupts": Register(1),
                 "halted": Register(1),
                 # flags
                 "z"  : SubRegister("af", 1, 7), 
                 "n"  : SubRegister("af", 1, 6),
                 "h"  : SubRegister("af", 1, 5),
                 "c"  : SubRegister("af", 1, 4)}

    def decode(self, state, stream):
        b = stream.read8()
        x = b >> 6
        y = (b >> 3) & 0x7
        z = b & 0x7
        p = y >> 1
        q = y & 1
        if x == 1:
            if y == 6 and z == 6:
                return Instruction("halt", {"pc": [add, "pc", 1], "halted": 1})
            else:
                return Instruction("ld %s, %s" % (regs[y], regs[z]),
                        {regs[y]: regs[z],
                         "pc": [add, "pc", 1]})
        if x == 2:
            if y == 0:
                return Instruction("add a,%s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [add, "a", regs[z]],
                         "z": [eq, [xorl, [add, "a", regs[z]], 0xff], 0],
                         "n": 0,
                         "h": [gt, [add, [xorl, "a", 0xf], [xorl, regs[z], 0xf]], 0xf],
                         "c": [gt, [add, "a", regs[z]], 0xff]})
            if y == 1:
                return Instruction("adc a,%s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [add, [add, "a", regs[z]], "c"],
                         "z": [eq, [xorl, [add, [add, "a", regs[z]], "c"], 0xff], 0],
                         "n": 0,
                         "h": [gt, [add, [add, [xorl, "a", 0xf], [xorl, regs[z], 0xf]], "c"], 0xf],
                         "c": [gt, [add, [add, "a", regs[z]], "c"], 0xff]})
            if y == 2:
                return Instruction("sub %s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [sub, "a", regs[z]],
                         "z": [eq, [mod, [sub, "a", regs[z]], 0xff], 0],
                         "n": 1,
                         "h": [gt, [add, [xorl, "a", 0xf], [xorl, regs[z], 0xf]], 0xf],
                         "c": [gt, [add, "a", regs[z]], 0xff]})
            if y == 3:
                return Instruction("sbc a,%s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [sub, [sub, "a", regs[z]], "c"],
                         "z": [eq, [mod, [sub, [sub, "a", regs[z]], "c"], 0xff], 0],
                         "n": 1,
                         "h": [gt, [sub, [sub, [xorl, "a", 0xf], [xorl, regs[z], 0xf]], "c"], 0xf],
                         "c": [gt, [sub, [sub, "a", regs[z]], "c"], 0xff]})
            if y == 4:
                return Instruction("and %s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [andl, "a", regs[z]],
                         "z": [eq, [andl, "a", regs[z]], 0],
                         "n": 0, "h": 1, "c": 0})
            if y == 5: 
                return Instruction("xor %s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [xorl, "a", regs[z]],
                         "z": [eq, [xorl, "a", regs[z]], 0],
                         "n": 0, "h": 0, "c": 0})
            if y == 6:
                return Instruction("or %s" % regs[z],
                        {"pc": [add, "pc", 1],
                         "a": [orl, "a", regs[z]],
                         "z": [eq, [orl, "a", regs[z]], 0],
                         "n": 0, "h": 0, "c": 0})
            if y == 7:
                return Instruction("cp %s" % regs[z], 
                        {"pc": [add, "pc", 1],
                         "z": [eq, [mod, [sub, "a", regs[z]], 0xff], 0],
                         "n": 1,
                         "h": [gt, [add, [xorl, "a", 0xf], [xorl, regs[z], 0xf]], 0xf],
                         "c": [gt, [add, "a", regs[z]], 0xff]}) 
        if x == 0:
            if z == 0:
                if y == 0:
                    return Instruction("nop", {"pc": [add, "pc", 1]})
                if y == 1:
                    nn = stream.read16()
                    return Instruction("ld 0x%04x,sp" % nn,
                            {Memory8(nn): "sp", "pc": [add, "pc", 3]})
                if y == 2:
                    return Instruction("stop", {"pc": [add, "pc", 1], "halted": 1})
                d = stream.read8s()
                if y == 3:
                    return Instruction("jr %i" % d, {"pc": [add, "pc", d+2]})
                if y == 4:
                    return Instruction("jr nz,%i" % d, 
                        {"pc": [if_, "z", 
                                    [add, "pc", 2], 
                                    [add, "pc", d+2]]})
                if y == 5:
                    return Instruction("jr z,%i" % d, 
                        {"pc": [if_, "z", 
                                    [add, "pc", d+2], 
                                    [add, "pc", 2]]})
                if y == 6:
                    return Instruction("jr nc,%i" % d, 
                        {"pc": [if_, "c", 
                                    [add, "pc", 2], 
                                    [add, "pc", d+2]]})
                if y == 7:
                    return Instruction("jr c,%i" % d, 
                        {"pc": [if_, "c", 
                                    [add, "pc", d+2], 
                                    [add, "pc", 2]]})
            if z == 1:
                if q == 0:
                    nn = stream.read16()
                    return Instruction("ld %s,0x%04x" % (regpairs[p], nn), 
                        {regpairs[p]: nn,
                         "pc": [add, "pc", 3]})
                if q == 1:
                    return Instruction("add hl,%s" % regpairs[p], 
                        {"hl": [add, "hl", regpairs[p]], 
                         "pc": [add, "pc", 1],
                         "n": 0,
                         # h is undefined for 16 bit adds
                         "c": [gt, [add, "hl", regpairs[p]], 0xffff]})
            if z == 2:
                return x0z2[y]
            if z == 3 and not q:
                return Instruction("inc %s" % regpairs[p], 
                        {regpairs[p]: [add, regpairs[p], 1],
                         "pc": [add, "pc", 1]})
            if z == 3 and q:
                return Instruction("dec %s" % regpairs[p], 
                        {regpairs[p]: [add, regpairs[p], 1], 
                         "pc": [add, "pc", 1]})
            if z == 4:
                return Instruction("inc %s" % regs[y], 
                        {regs[y]: [add, regs[y], 1],
                         "pc": [add, "pc", 1],
                         "z": [eq, regs[y], 0xff],
                         "n": 0,
                         "h": [eq, [xorl, regs[y], 0xf], 0xf]})
            if z == 5:
                return Instruction("dec %s" % regs[y], 
                        {regs[y]: [sub, regs[y], 1], 
                         "pc": [add, "pc", 1],
                         "z": [eq, regs[y], 0x01],
                         "n": 1,
                         "h": [eq, [xorl, regs[y], 0xf], 0x0]})
            if z == 6:
                n = stream.read8()
                return Instruction("ld %s,0x%02x" % (regs[y],n), 
                    {regs[y]: n, 
                     "pc": [add, "pc", 2]})
            if z == 7:
                return x0z7[y]
        if x == 3:
            if z == 0:
                if y == 0:
                    return Instruction("ret nz", 
                        {"pc": [if_, "z", 
                                    [add, "pc", 1], 
                                    Memory16("sp")],
                         "sp": [if_, "z",
                                    None,  # None means nothing happens
                                    [add, "sp", 2]]})
                if y == 1:
                    return Instruction("ret z", 
                        {"pc": [if_, "z", 
                                    Memory16("sp"),
                                    [add, "pc", 1]],
                         "sp": [if_, "z",
                                    [add, "sp", 2],
                                    None]}) # None means nothing happens
                if y == 2:
                    return Instruction("ret nc", 
                        {"pc": [if_, "c", 
                                    [add, "pc", 1], 
                                    Memory16("sp")],
                         "sp": [if_, "c",
                                    None, # None means nothing happens
                                    [add, "sp", 2]]})
                if y == 3:
                    return Instruction("ret c", 
                        {"pc": [if_, "c", 
                                    Memory16("sp"),
                                    [add, "pc", 1]],
                        "sp": [if_, "c",
                                    [add, "sp", 2],
                                    None]}) # None means nothing happens
                if y == 4:
                    n = stream.read8()
                    return Instruction("ld (0xff00 + 0x%02x), a" % n, 
                        {Memory8(0xff00+n): "a", 
                         "pc": [add, "pc", 2]})
                if y == 5:
                    d = stream.read8s()
                    return Instruction("add sp,%i" % d, 
                        {"sp": [add, "sp", d], 
                         "pc": [add, "pc", 2],
                         "z": 0,
                         "n": 0,
                         # h is undefined for 16 bit adds
                         "c": [gt, [add, "sp", d], 0xffff]}) # Question, what happens on underflow?
                if y == 6:
                    n = stream.read8()
                    return Instruction("ld a,(0xff00+0x%02x)" % n, 
                        {"a": Memory8(0xff00+n), 
                         "pc": [add, "pc", 2]})
                if y == 7:
                    d = stream.read8s()
                    return Instruction("ld hl,sp+%i" % d,
                        {"hl": [add, "sp", d], 
                         "pc": [add, "pc", 2]})
            if z == 1:
                if q == 0:
                    return Instruction("pop %s" % regpairs[p],
                        {"pc": [add, "pc", 1],
                         regpairs[p]: Memory16("sp"), 
                         "sp": [add, "sp", 2]})
                if p == 0:
                    return Instruction("ret", 
                        {"pc": Memory16("sp"), 
                         "sp": [add, "sp", 2]})
                if p == 1:
                    return Instruction("reti", 
                        {"pc": Memory16("sp"), 
                         "sp": [add, "sp", 2]})
                if p == 2:
                    return Instruction("reti", 
                        {"pc": Memory16("sp"), 
                         "sp": [add, "sp", 2]})
                if p == 3:
                    return Instruction("ld sp, hl", 
                        {"sp": "hl", 
                         "pc": [add, "pc", 1]})
            if z == 2:
                if y == 0:
                    nn = stream.read16()
                    return Instruction("jp nz,0x%04x" % nn, 
                        {"pc": [if_, "z", 
                                    [add, "pc", 3], 
                                    nn],
                         "sp": [add, "sp", 2]})
                if y == 1:
                    nn = stream.read16()
                    return Instruction("jp z,0x%04x" % nn,
                        {"pc": [if_, "z", 
                                    nn,
                                    [add, "pc", 3]]})
                if y == 2:
                    nn = stream.read16()
                    return Instruction("jp nc,0x%04x" % nn,
                        {"pc": [if_, "c", 
                                    [add, "pc", 3], 
                                    nn]})
                if y == 3:
                    nn = stream.read16()
                    return Instruction("jp c,0x%04x" % nn,
                        {"pc": [if_, "c", 
                                    nn,
                                    [add, "pc", 3]]})
                if y == 4:
                    return Instruction("ld (0xff00+c),a", 
                        {Memory8([add, 0xff00, "c"]): "a",
                         "pc": [add, "pc", 1]})
                if y == 5:
                    nn = stream.read16()
                    return Instruction("ld (0x%04x),a" % nn, 
                        {Memory8(nn): "a",
                         "pc": [add, "pc", 3]})
                if y == 6:
                    return Instruction("ld a,(0xff00+c)", 
                        {"a": Memory8([add, 0xff00, "c"]),
                         "pc": [add, "pc", 1]})
                if y == 7:
                    nn = stream.read16()
                    return Instruction("ld a,(0x%04x)" % nn, 
                        {"a": Memory8(nn),
                         "pc": [add, "pc", 3]})
            if z == 3:
                if y == 0:
                    nn = stream.read16()
                    return Instruction("jp 0x%04x" % nn, {"pc": nn})
                if y == 1:
                    return self.CBdecode(stream.read8())
                if y == 6:
                    return Instruction("di", 
                        {"interupts": 0,
                         "pc": [add, "pc", 1]})
                if y == 7:
                    return Instruction("ei", 
                        {"interupts": 1, 
                         "pc": [add, "pc", 1]})
            if z == 4:
                if y == 0:
                    nn = stream.read16()
                    return Instruction("call nz", 
                        {"pc": [if_, "z", 
                                    [add, "pc", 3], 
                                    nn],
                        Memory16([sub, "sp", 2]): [if_, "z",
                                    None,  # None means nothing happens
                                    [add, "pc", 3]],
                         "sp": [if_, "z",
                                    None,
                                    [sub, "sp", 2]]})
                if y == 1:
                    nn = stream.read16()
                    return Instruction("call z", 
                        {"pc": [if_, "z", 
                                    nn,
                                    [add, "pc", 3]],
                         Memory16([sub, "sp", 2]): [if_, "z",
                                    [add, "pc", 3],
                                    None], # None means nothing happens
                         "sp": [if_, "z",
                                    [sub, "sp", 2],
                                    None]})
                if y == 2:
                    nn = stream.read16()
                    return Instruction("call nc", 
                        {"pc": [if_, "c", 
                                    [add, "pc", 3], 
                                    nn],
                         Memory16([sub, "sp", 2]): [if_, "c",
                                    None,
                                    [add, "pc", 3]],
                         "sp": [if_, "c",
                                    None,
                                    [sub, "sp", 2]]})
                if y == 3:
                    nn = stream.read16()
                    return Instruction("call c", 
                        {"pc": [if_, "c", 
                                    nn,
                                    [add, "pc", 1]],
                        Memory16([sub, "sp", 2]): [if_, "c",
                                    [add, "pc", 3],
                                    None], # None means nothing happens
                         "sp": [if_, "c",
                                    [sub, "sp", 2],
                                    None]})
            if z == 5:
                if q == 0:
                    return Instruction("push %s" % regpairs[p], 
                        {"pc": [add, "pc", 1],
                         Memory16([sub, "sp", 2]): regpairs[p],
                         "sp": [sub, "sp", 2]})
                if p == 0:
                    nn = stream.read16()
                    return Instruction("call 0x%04x" % nn, 
                        {"pc": nn,
                         Memory16([sub, "sp", 2]): [add, "pc", 3],
                         "sp": [sub, "sp", 2]})
            if z == 6:
                n = stream.read8()
                if y == 0:
                    return Instruction("add a,0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [add, "a", n],
                         "z": [eq, [xorl, [add, "a", n], 0xff], 0],
                         "n": 0,
                         "h": [gt, [add, [xorl, "a", 0xf], n ^ 0xf], 0xf],
                         "c": [gt, [add, "a", n], 0xff]})
                if y == 1:
                    return Instruction("adc a,0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [add, [add, "a", n], "c"],
                         "z": [eq, [xorl, [add, [add, "a", n], "c"], 0xff], 0],
                         "n": 0,
                         "h": [gt, [add, [add, [xorl, "a", 0xf], n^0xf], "c"], 0xf],
                         "c": [gt, [add, [add, "a", n], "c"], 0xff]})
                if y == 2:
                    return Instruction("sub 0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [sub, "a", n],
                         "z": [eq, [mod, [sub, "a", n], 0xff], 0],
                         "n": 1,
                         "h": [gt, [add, [xorl, "a", 0xf], n^0xf], 0xf],
                         "c": [gt, [add, "a", n], 0xff]})
                if y == 3:
                    return Instruction("sbc a,0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [sub, [sub, "a", n], "c"],
                         "z": [eq, [mod, [sub, [sub, "a", n], "c"], 0xff], 0],
                         "n": 1,
                         "h": [gt, [sub, [sub, [xorl, "a", 0xf], n^0xf], "c"], 0xf],
                         "c": [gt, [sub, [sub, "a", n], "c"], 0xff]})
                if y == 4:
                    return Instruction("and 0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [andl, "a", n],
                         "z": [eq, [andl, "a", n], 0],
                         "n": 0, "h": 1, "c": 0})
                if y == 5: 
                    return Instruction("xor 0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [xorl, "a", n],
                         "z": [eq, [xorl, "a", n], 0],
                         "n": 0, "h": 0, "c": 0})
                if y == 6:
                    return Instruction("or 0x%02x" % n,
                        {"pc": [add, "pc", 2],
                         "a": [orl, "a", n],
                         "z": [eq, [orl, "a", n], 0],
                         "n": 0, "h": 0, "c": 0})
                if y == 7:
                    return Instruction("cp 0x%02x" % n, 
                        {"pc": [add, "pc", 2],
                         "z": [eq, [mod, [sub, "a", n], 0xff], 0],
                         "n": 1,
                         "h": [gt, [add, [xorl, "a", 0xf], n^0xf], 0xf],
                         "c": [gt, [add, "a", n], 0xff]}) 
            if z==7:
                return Instruction("rst 0x%02x" % y*8, 
                        {"pc": y*8,
                         Memory16([sub, "sp", 2]): [add, "pc", 1],
                         "sp": [sub, "sp", 2]})

    def CBdecode(self, b):
        x = b >> 6
        y = (b >> 3) & 0x7
        z = b & 0x7
        if x == 0:
            if y == 0:
                return Instruction("rlc %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [rotleft, 1, 8, regs[z]],
                         "z": [eq, regs[z], 0],
                         "c": [bit, 7, regs[z]],
                         "n": 0, "h": 0})
            if y == 1:
                return Instruction("rrc %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [rotright, 1, 8, regs[z]],
                         "z": [eq, regs[z], 0],
                         "c": [bit, 0, regs[z]],
                         "n": 0, "h": 0})
            if y == 2:
                return Instruction("rl %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [orl, [shiftleft, 1, regs[z]], "c"],
                         "z": [eq, [orl, [xorl, regs[z], 0x7f], "c"], 0],
                         "c": [bit, 7, regs[z]],
                         "n": 0, "h": 0})
            if y == 3:
                return Instruction("rr %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [orl, [shiftright, 1, regs[z]], [shiftleft, "c", 7]],
                         "z": [eq, [orl, [shiftright, 1, regs[z]], "c"], 0],
                         "c": [bit, 0, regs[z]],
                         "n": 0, "h": 0})
            if y == 4:
                return Instruction("sla %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [shiftleft, 1, regs[z]],
                         "z": [eq, [xorl, regs[z], 0x7f], 0],
                         "c": [bit, 7, regs[z]],
                         "n": 0, "h": 0})
            if y == 5:
                return Instruction("sra %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [orl, [shiftright, 1, regs[z]], [xorl, regs[z], 0x80]],
                         "z": [lt, regs[z], 2],
                         "c": [bit, 0, regs[z]],
                         "n": 0, "h": 0})
            if y == 6:
                return Instruction("swap %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [orl, [shiftleft, 4, regs[z]], [shiftright, 4, regs[z]]],
                         "z": [eq, regs[z], 0],
                         "n": 0, "h": 0, "c": 0})
            if y == 7:
                return Instruction("srl %s" % regs[z],
                        {"pc": [add, "pc", 2],
                         regs[z]: [shiftright, 1, regs[z]],
                         "z": [lt, regs[z], 2],
                         "c": [bit, 0, regs[z]],
                         "n": 0, "h": 0})
        if x == 1:
            return Instruction("bit %i,%s" % (y, regs[z]),
                        {"pc": [add, "pc", 2],
                         "z": [bit, y, regs[z]],
                         "n": 0, "h": 0})
        if x == 2:
            return Instruction("set %i,%s" % (y, regs[z]),
                        {"pc": [add, "pc", 2],
                         regs[z]: [orl, regs[z], 1 << y]})
        if x == 3: Instruction("res %i,%s" % (y, regs[z]),
                        {"pc": [add, "pc", 2],
                         regs[z]: [xorl, regs[z], ~(1 << y)]})


