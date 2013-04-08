#!/usr/bin python
# -*- coding: UTF-8 -*-
# convert_tzyh_to_UTF7_py26.py
# 20100530, works.
# David Prager Branenr
'''
Revises program "convert_tzyh_to_UTF6.py" to include treatment of surrogate pairs.

Demonstrates six methods:

    to convert a Chinese character to its Unicode codepoint (base 10);

    to convert a codepoint to the corresponding Chinese character;

    to convert surrogate pairs to a single scalar codepoint;

    to convert a single scalar codepoint to a surrogate pair;

    to convert a string of Chinese to a string of codepoints, (surrogate pairs to scalars;

    to convert a string of codepoints (including scalars) to a string of Chinese characters.

Data from http://www.russellcottrell.com/greek/utilities/SurrogatePairCalculator.htm on 20100515. © David Prager Branner, date of code: 20100530. Works, but check the "wrong order" and other surrogate pair code, which may still have issues — do this by intentionally reversing pairs or omitting one member.
'''

import math

class Codepoint(object):
    def __init__(self):
        return

    def tz2u(self, tz):
        '''Converts a single tzyh to the corresponding codepoint.'''
        self.tz = tz
        self.u = eval('u\''+str(ord(self.tz))+'\'')
        return self.u

    def u2tz(self, u):
        '''Converts a single codepoint (decimal) to the corresponding tzyh.'''
        self.u = u
        # unichr() can't handle these in narrow Python build
        if u > 65535: 
            hi_surr, lo_surr = self.S_to_HL(u)
            self.tz = unichr(hi_surr) + unichr(lo_surr)
        else:
            self.tz = unichr(u)
        return self.tz.encode('utf-8')

    def tz2u_str(self, mystring):
        '''Converts string of tzyh to a string of space-separated codepoints.'''
        codepoint_str = ''
        for tzyh in mystring:
            try:
                codepoint_str += self.tz2u(tzyh) +' '
            except Exception, e:
                print e, 'in tz2u_str'
        # now deal with surrogate pairs
        #   first check if there is any surrogate at all
        #     if so, check if the following one is low
        #       if so, call HL_to_S(first, second)
        #       if not, then check if there is a pair in the wrong order
        #       if so, reverse them and call HL_to_S(first, second)
        # GGG NEEDS TO BE TESTED NOW.
        for item in codepoint_str.split():
            item_int = int(item.strip())
            if 55296 <= item_int <= 57343:
                # then it is some surrogate, whether high or low
                # now select only that and the next index
                # do so by stripping all before and all after, but don't discard
                start, junk, rightremnant = codepoint_str.partition(item+' ')
                # end of string has been reached; can't continue
                if rightremnant == '': 
                    continue
                next_item, junk, end = rightremnant.partition(' ')
                next_item_int = int(next_item.strip())
                if ((55296 <= item_int <= 56319) and 
                        (56320 <= next_item_int <= 57343)):
                    # then is surrogate pair so send to HL_to_S(item_int, 
                    # next_item_int)
                    codepoint_str = (start + str(self.HL_to_S(item_int, 
                            next_item_int)) + ' ' + end)
                    pass
                # otherwise, check if 2 surrogates are in wrong order;
                #    if so, assume correct and reverse them, but 
                #    could lead to error
                elif ((55296 <= next_item_int <= 56319) and 
                        (56320 <= item_int <= 57343)):
                    item_int, next_item_int = next_item_int, item_int
                    # send to HL_to_S(item_int, next_item_int)
                    codepoint_str = (start + str(self.HL_to_S(item_int, 
                            next_item_int)) + ' ' + end)
                # now check if only one isolated surrogate, not one of pair
                elif (((55296 <= item_int <= 56319) and not 
                        (56320 <= next_item_int <= 57343)) or 
                        (56320 <= next_item_int <= 57343) and not (55296 <=
                            item_int <= 56319)):
                    # in that case discard line
                    codepoint_str = ''
                    pass
        return codepoint_str.rstrip() # remove final space at end
    #           Experiment on surrogate pairs 55379 56832 55379 56833 55379 56834 55379 56835

    def u2tz_str(self, codepoint_str):
        '''Converts string of space-separated codepoints to a string of tzyh.'''
        reconst_str = ''
        for item in codepoint_str.split():
            try:
                # Decoding is necessary or Python thinks the string is ASCII
                #   Has to be here; too late at print-time.
                reconst_str += self.u2tz(int(item)).decode('utf-8')
            except Exception, e:
                print e, 'in u2tz_str'
        return reconst_str
    # deal with surrogate pairs
    # if one of each is present, combine to form single codepoint
    # (Surrogates should be combined only after conversion to codepoint string)
    # ( but before returning codepoint string)
    # ( and before conversion to tzyh string but before returning tzyh string.)
    #    loop: if index in range() and index+1 in range(), then do math

    def HL_to_S(self, hi_surr, lo_surr):
        '''Converts a surrogate pair to a single scalar codepoint (decimal).'''
        self.hi_surr, self.lo_surr = hi_surr, lo_surr
        # Hex ranges 0xD800–0xDBFF for high surrogate, 
        # 0xDC00-0xDFFF low surrogate
        # Decimal ranges 55296-56319 for high surrogate, 
        #56320-57343 for low surrogate
        # is not high surrogate
        if self.hi_surr < 55296 or self.hi_surr > 56319: 
            return
        # is not low surrogate
        if self.lo_surr < 56320 or self.lo_surr > 57343: 
            return
        # S = (H - D800) * 400+ (L - DC00) + 10000 , hex
        self.scalar = (((self.hi_surr - 55296) *1024) + 
                (self.lo_surr - 56320) + 65536)
        return self.scalar
        # Tested on:
        #   𤸀𤸁𤸂𤸃 — 151040 151041 151042 151043
        #   Surrogate pairs 55379, 56832; 55379, 56833; 55379 56834 55379 56835
        #   𠩶𠩷𠩸𠩹 - 133750 133751 133752 133753
        #   Surrogate pairs 55362, 56950; 55362, 56951; 55362, 56952; 55362, 56953;
        #   𡿾𡿿𢀀𢀁 - 139262 139263 139264 139265
        #   Surrogate pairs 55367, 57342; 55367, 57343; 55368, 56320; 55368, 56321;


    def S_to_HL(self, scalar):
        '''Converts a single scalar codepoint to a surrogate pair (decimal).'''
        self.scalar = scalar
        if self.scalar < 65536: # because then does not need surrogate pairs
            return
        # H = S/400 + D800 , hex
        self.hi_surr = int(math.floor((self.scalar - 65536)/1024)) + 55296
        # L = S%400 + DC00 , hex
        self.lo_surr = (self.scalar - 65536)%1024 + 56320
        return self.hi_surr, self.lo_surr
        # Tested on:
        #   𤸀𤸁𤸂𤸃 — 151040 151041 151042 151043
        #   Surrogate pairs 55379 56832 55379 56833 55379 56834 55379 56835
        #   𠩶𠩷𠩸𠩹 - 133750 133751 133752 133753
        #   Surrogate pairs 55362 56950 55362 56951 55362 56952 55362 56953
        #   𡿾𡿿𢀀𢀁 - 139262 139263 139264 139265
        #   Surrogate pairs 55367 57342 55367 57343 55368 56320 55368 56321
        #   if only one is present, whole line must be discarded!

def main():
    tryme = Codepoint()
    mystring = raw_input('Input tzyh: ').decode('utf-8')
    # first, convert to a string of codepoints
    result1 = tryme.tz2u_str(mystring)
    print 'Converts to these codepoints:', result1
    # then, convert back to original string
    result2 = tryme.u2tz_str(result1)
    print 'Reconverts to this string:', result2
    #    print 'Original length was %d; 
    # new length is %d.' % (len(mystring), len(result2))

if __name__=='__main__':
    main()
