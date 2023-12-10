from random import shuffle, choices


class BadInputError(Exception):
    def __init__(self, player_len):
        options = {1: '1 only', 2: '1 or 2 only'}
        self.msg = f'Invalid input. Please try again.\n' \
                   f'You can choose {options.get(player_len, "from 1 to {}".format(player_len))}.'
        super().__init__(self.msg)


class IllegalMoveError(Exception):
    def __init__(self, valid, serp_ends):
        options = ["Either side valid -> {}", "{} <-L valid R > {}"]
        valid_display = [', '.join(map(str, valid_side)) or None for valid_side in valid]
        self.msg = f'Illegal move. Please try again.\n' \
                   f'{options[len(set(serp_ends)) - 1].format(*valid_display)}. ' \
                   f'{(m := "Pulling from stock -> 0.")[:set(valid_display) == {None} and len(m)]}'

    def __str__(self):
        return self.msg


class Domino:
    SPLIT_LNE = '=' * 70
    STATS_LNE = '{head}\nStock size: {0}\nComputer size: {1}\n\n{serp}\n\nPlayer pieces:\n{2}\n{opt_lne}Status:'
    SERP_MASK = '...'
    MASK_CRIT, UPPER_KEY, DRAW_CRIT = range(6, 9)

    def __init__(self, hand):
        self.hand = hand
        self.player = self.computer = []
        self.left_end = self.right_end = self.serp_ends = self.draw = None
        self.serp = choices(doubles := [
            [i] * 2 for i in range(self.UPPER_KEY)], [2 ** i for i in range(len(doubles))])
        self.stock = [[i, j] for i in range(self.UPPER_KEY) for j in range(i, self.UPPER_KEY)]

    def get_cmd(self, playing):
        while True:
            try:
                dom_num = input()
                if playing is self.player and not all((len(dom_num), dom_num.lstrip('-').isdigit())) or \
                        abs(int(dom_num)) > len(self.player):
                    raise BadInputError(len(self.player))
                if not set(self.player[abs(int(dom_num)) - 1]) & {self.serp_ends[int(dom_num) > 0]} and \
                        dom_num != '0':
                    valid = [[dom for dom in self.player if set(dom) & {dom_end}] for dom_end in self.serp_ends]
                    raise IllegalMoveError(valid, self.serp_ends)
                return int(dom_num)
            except (BadInputError, IllegalMoveError) as err:
                print(err)
            except ValueError:
                return self.get_ai_cmd()

    def get_ai_cmd(self):
        options = (self.computer.index(dom) + 1 for dom in self.computer if set(dom) & set(self.serp_ends))
        for dom_num in options:
            if len(set(self.serp_ends)) - 1:
                return dom_num * [1, -1][len(set(self.computer[dom_num - 1]) & {self.left_end})]
            return dom_num * choices((1, -1))[0]
        return 0

    def allocate(self):
        while any(dom >= self.serp[0] for dom in self.stock[self.hand * 2:]
                  if len(set(dom)) == 1) or self.stock.remove(self.serp[0]):
            shuffle(self.stock)
        self.stock, self.player, self.computer = \
            [self.stock[:self.hand * 2]] + [self.stock[i: i + self.hand] \
                                            for i in range(self.hand * 2, len(self.stock), self.hand)]
        self.player, self.computer = [self.player, self.computer][::choices((1, -1))[0]]

    def stats(self, playing, game, serp_end=MASK_CRIT // 2):
        player_data = '\n'.join(f'{i}: {dom}' for i, dom in enumerate(self.player, 1))
        print(self.STATS_LNE
              .format(len(self.stock), len(self.computer), player_data,
                      head=self.SPLIT_LNE, opt_lne='\n'[:len(self.player) ^ 0],
                      serp=''.join(map(str, self.serp))
                      .replace(('-1', ''.join(map(str, self.serp[serp_end:len(self.serp) - serp_end]))
                                )[len(self.serp) > self.MASK_CRIT], self.SERP_MASK)), end=' ')

        if game:
            print(('Computer is about to make a move. Press Enter to continue...',
                   'It\'s your turn to make a move. Enter your command.'
                   )[playing == self.player])
        else:
            print(' '.join(('The game is over.', (
                ('You won!', 'The computer won!'), ('It\'s a draw!',) * 2
            )[self.draw & all((self.player, self.computer))][len(self.player) and 1])))

    def make_move(self, playing, dom_num):
        if dom_num:
            self.serp.insert((0, len(self.serp))[dom_num > 0],
                             self.opt_flip(playing.pop(abs(dom_num) - 1), dom_num))
        elif self.stock:
            playing.append(self.stock.pop())

    def opt_flip(self, dom, dom_num):
        is_action = [dom_end != snake_end for dom_end, snake_end in zip(dom[::-1], self.serp_ends)][dom_num > 0]
        return dom[::[1, -1][is_action]]

    def check_game_status(self):
        crit = (-1, self.left_end)[len({self.left_end, self.right_end}) % 2]
        self.draw = sum(self.serp, []).count(crit) > self.DRAW_CRIT - 1
        return all((self.player, self.computer, not self.draw))

    def update_serp_ends(self):
        self.left_end, *_, self.right_end = sum(self.serp, [])
        self.serp_ends = self.left_end, self.right_end

    def run(self, game=True):
        self.allocate()
        self.update_serp_ends()
        curr_player = (self.player, self.computer)[len(self.player) < len(self.computer)]

        while game:
            self.stats(curr_player, game)

            self.make_move(playing=curr_player, dom_num=self.get_cmd(playing=curr_player))
            self.update_serp_ends()

            game = self.check_game_status()
            curr_player = (self.player, self.computer)[curr_player == self.player]

        self.stats(curr_player, game)


my_game = Domino(7)
my_game.run()
