from random import choice, choices, shuffle


class BadInputError(Exception):
    def __init__(self, range_):
        self.range_ = range_

    def __str__(self):
        return f'Invalid input. Please try again. Expected nums in range: {self.range_}'


class IllegalMoveError(Exception):
    def __init__(self, options):
        self.message = f'Illegal move. Please try again. Valid options: {options}'
        super().__init__(self.message)


class Domino:
    up_key, ends_criteria, ends, mask = 7, 8, 3, '...'

    def __init__(self, hand):
        self.hand = hand
        self.player = self.computer = []
        self.snake = choices(doubles := [[i] * 2 for i in range(self.up_key)], [2 ** i for i in range(len(doubles))])
        self.snake_left_end = self.snake_right_end = self.snake_ends = None
        self.stock = [[i, j] for i in range(self.up_key) for j in range(i, self.up_key) if [i, j]]

    def allocate(self):
        while any(dom >= self.snake[0] for dom in self.stock[self.hand * 2:] if len(set(dom)) % 2) or \
                self.stock.remove(self.snake[0]):
            shuffle(self.stock)

        self.stock, self.player, self.computer = [self.stock[:self.hand * 2]] + \
                                                 [self.stock[i:i + self.hand] for i in range(
                                                     self.hand * 2, len(self.stock), self.hand)][::choice((-1, 1))]

    def stats(self, game, curr_player):
        print('{}\nStock size: {}\nComputer pieces: {}\n\n{}\n\nPlayer pieces:\n{}\n{}'.format(
            '=' * ord('f'.upper()), len(self.stock), len(self.computer),
            ''.join(map(str, self.snake)) if len(self.snake) < self.ends * 2 + 1 else
            ''.join(map(str, self.snake)).replace(
                ''.join(map(str, self.snake[self.ends:len(self.snake) - self.ends])), self.mask),
            '\n'.join([f'{i}: {e}' for i, e in enumerate(self.player, 1)]),
            '\nStatus:'), end=' ')
        print(('Computer is about to make a move. Press Enter to continue...',
               'It\'s your turn to make a move. Enter your command.')
              [curr_player == self.player] if game else '\nThe game is over.', end=' ')

    def get_command(self):
        while True:
            dom_ind = input()
            try:
                if not dom_ind.lstrip('-').isdigit() and len(dom_ind) or abs(int(dom_ind)) > len(self.player):
                    raise BadInputError(f'{-len(self.player)}...{len(self.player)}')
                dom_ind = int(dom_ind)
                if dom_ind > 0 and self.snake_right_end not in self.player[dom_ind - 1] or \
                        dom_ind < 0 and self.snake_left_end not in self.player[abs(dom_ind) - 1]:
                    user_options = [
                        [str(opt) for opt in self.player if set(opt) & {snake_end}] for snake_end in self.snake_ends]
                    raise IllegalMoveError(f'{" ".join(user_options[0]) or None} < left | '
                                           f'right > {" ".join(user_options[1]) or None}')
            except (BadInputError, IllegalMoveError) as err:
                print(err); continue
            except ValueError:
                return self.get_ai_command()
            return dom_ind

    def make_move(self, playing, dom_ind):
        if dom_ind:
            self.snake.insert((0, len(self.snake))[dom_ind > 0], self.flip(playing.pop(abs(dom_ind) - 1), dom_ind))
            return
        if self.stock:
            playing.append(self.stock.pop())

    def flip(self, dom, dom_ind):
        if dom_ind > 0 and self.snake_right_end != dom[0] or dom_ind < 0 and self.snake_left_end != dom[1]:
            return dom[::-1]
        return dom

    def get_ai_command(self):
        ai_options = [opt for opt in self.computer if set(opt) & set(self.snake_ends)]
        if ai_options:
            ai_choice: list = choice(ai_options)
            any_side: bool = sum(self.snake_ends.count(x) for x in set(ai_choice)) == 2
            ai_dom_ind: int = self.computer.index(ai_choice) + 1
            ai_dom_ind *= [(-1, 1), (choice((-1, 1)),) * 2][any_side][self.snake_right_end in ai_choice]
        else:
            ai_dom_ind = 0
        return ai_dom_ind

    def update_snake_ends(self):
        self.snake_left_end, *_, self.snake_right_end = sum(self.snake, [])
        self.snake_ends = [self.snake_left_end, self.snake_right_end]

    def check_game_status(self):
        criteria = (-1, self.snake_left_end)[len({self.snake_right_end, self.snake_left_end}) % 2]
        ends_less_8: bool = sum(self.snake, []).count(criteria) < self.ends_criteria
        return all((self.computer, self.player, ends_less_8))

    def main(self, game=True):
        self.allocate()
        curr_player = (self.player, self.computer)[len(self.player) < len(self.computer)]
        while game:
            self.update_snake_ends()
            self.stats(game, curr_player)
            self.make_move(playing=curr_player, dom_ind=self.get_command())
            curr_player = (self.player, self.computer)[curr_player == self.player]
            game = self.check_game_status()
        self.stats(game, curr_player)
        print((('You won!!', 'The computer won!'), ('It\'s a draw!',) * 2)
              [all((self.computer, self.player))][curr_player == self.player])


my_game = Domino(7)
my_game.main()
