#!/usr/bin/python

from copy import deepcopy


class Series:

    def __init__(self, series, share_quantity, preference, convertible, participating, seniority):
        self.series = series
        self.share_quantity = share_quantity
        self.preference_per_share = preference
        self.payout = 0
        self.seniority = seniority

        self.participating = participating
        if participating or not convertible:
            self.converts = False
        else:
            self.can_convert = convertible
            self.converts = None
            self.participating = None

    def __bool__(self):
        return self.converts is not None

    def __repr__(self):
        if self.converts:
            return (
                f"<Common quantity='{self.share_quantity}' payout_per="
                f"'{self.payout / self.share_quantity}'>"
            )
        return (
            f"<Series {self.series} preferred quanity='{self.share_quantity}' preference_per="
            f"'{self.preference_per_share}' payout_per='{self.payout / self.share_quantity}'>"
        )

    def preference_total(self):
        return self.preference_per_share * self.share_quantity

    def would_convert(self, payout_total, common_total, options, junior):
        if self.converts is not None:
            if not junior:
                return [self.converts]
            return [self.converts] + junior[0].would_convert(
                payout_total,
                common_total,
                options,
                junior[1:]
            )

        if not junior:
            payout_total += self.payout
            common_total += self.share_quantity
            if payout_total / common_total * self.share_quantity < self.payout:
                return [False]
            payout_adjusted, common_adjusted, _ = adjust_options(
                payout_total,
                common_total,
                options
            )
            return [payout_adjusted / common_adjusted * self.share_quantity > self.payout]

        convert_results = junior[0].would_convert(
            payout_total + self.payout,
            common_total + self.share_quantity,
            options,
            junior[1:]
        )
        adjusted_common, adjusted_payout = common_total, payout_total
        for i, p in zip(convert_results, junior):
            if i:
                adjusted_common += p.share_quantity
                adjusted_payout += p.payout

        if adjusted_payout / adjusted_common * self.share_quantity < self.payout:
            return [False] + junior[0].would_convert(
                payout_total,
                common_total,
                options,
                junior[1:]
            )
        adjusted_payout, adjusted_common, _ = adjust_options(
            adjusted_payout,
            adjusted_common,
            options
        )
        if adjusted_payout / adjusted_common * self.share_quantity > self.payout:
            return [True] + convert_results
        return [False] + junior[0].would_convert(payout_total, common_total, options, junior[1:])

    def set_payout(self, per_share):
        payout = self.share_quantity * per_share
        self.payout += payout
        return payout


class Option:

    def __init__(self, quantity, call_value):
        self.quantity = quantity
        self.call_value = call_value

    def in_the_money(self, common_total, payout):
        return payout / (self.quantity + common_total) > self.call_value

    def total(self):
        return self.call_value * self.quantity

    def adjusted_payout(self, per_share):
        return (per_share - self.call_value) * self.quantity

    def set_payout(self, per_share):
        self.payout = (per_share - self.call_value) * self.quantity
        return self.payout

    def __repr__(self):
        return (
            f"<Option call_value='{self.call_value}' quantity='{self.quantity}'"
            f", payout_per='{self.payout / self.quantity}>"
        )


preferred = [  # quantity, pref_per, convertible, participating, seniority
    Series('A', 10000, 10, True, False, 1),
    Series('B', 10000, 11, True, True, 1),
    Series('C', 10000, 15, True, False, 2),
    Series('D', 10000, 20, True, False, 2)
]
options = [
    Option(10000, 10),
    Option(10000, 100),
    Option(10000, 1),
    Option(10000, 1000)
]


def run(payout, common, options, preferred):

    options = deepcopy(options)
    preferred = deepcopy(preferred)
    participating = [Series('.', common, 0, False, True, False)]
    participating[0].converts = True

    # remove preference amounts from payout
    seniority = [
        [p for p in preferred if p.seniority == i] for i in
        sorted(set(x.seniority for x in preferred), reverse=True)
    ]
    for level in seniority:
        total = sum(i.preference_total() for i in level)
        if payout <= total:
            pct = payout / total
            payout = 0
            for p in level:
                p.payout = p.preference_total() * pct
            payout = 0
            participating.clear()
            break
        payout -= total
        for p in level:
            p.payout = p.preference_total()
            if p.participating:
                participating.insert(0, p)
                common += p.share_quantity

    converts = preferred[-1].would_convert(payout, common, options, preferred[-2::-1])
    converts.reverse()

    ## finished up to here

    for i in range(len(converts)):
        if preferred[i].converts is not None:
            continue
        p = preferred[i]
        p.converts = converts[i]
        if converts[i]:
            payout += p.payout
            p.payout = 0
            participating.append(p)

    if payout:
        payout_adjusted, common_adjusted, options = adjust_options(
            payout,
            sum(i.share_quantity for i in participating),
            options
        )
        per_share = payout_adjusted / common_adjusted
        participating.extend(options)
    else:
        per_share = 0
    for p in participating:
        payout_adjusted -= p.set_payout(per_share)

    print('\n\npreferred descending...')
    for i in preferred[::-1]:
        print(i)
    print('\nparticipating...')
    for i in participating:
        print(i)


def adjust_options(payout, common, options):
    options = sorted(options, key=lambda k: k.call_value)
    for i in range(len(options)):
        if not options[i].in_the_money(common, payout):
            return payout, common, options[:i]
        payout += options[i].total()
        common += options[i].quantity
    # pay pool if options are claimed, total common stock with claimed options,
    return payout, common, options
