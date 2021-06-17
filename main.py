import cProfile
import csv
from enum import Enum
import random

class PrizeClass(Enum):
  SEVEN = 'SEVEN'
  SIX_PLUS = 'SIX_PLUS'
  SIX = 'SIX'
  FIVE_PLUS = 'FIVE_PLUS'
  FIVE = 'FIVE'
  FOUR_PLUS = 'FOUR_PLUS'
  FOUR = 'FOUR'
  THREE_PLUS = 'THREE_PLUS'
  THREE = 'THREE'

  def for_matches(num_matches, bonus):
    if num_matches == 7:
      return PrizeClass.SEVEN
    elif num_matches == 6 and bonus:
      return PrizeClass.SIX_PLUS
    elif num_matches == 6:
      return PrizeClass.SIX
    elif num_matches == 5 and bonus:
      return PrizeClass.FIVE_PLUS
    elif num_matches == 5:
      return PrizeClass.FIVE
    elif num_matches == 4 and bonus:
      return PrizeClass.FOUR_PLUS
    elif num_matches == 4:
      return PrizeClass.FOUR
    elif num_matches == 3 and bonus:
      return PrizeClass.THREE_PLUS
    elif num_matches == 3:
      return PrizeClass.THREE
    else:
      return None

class Play:
  def __init__(self, numbers):
    if len(numbers) != 7:
      raise Error('Incorrect number of numbers in play')
    self.numbers = numbers

  def generate():
    numbers = set(random.sample(range(1, 51), 7))
    return Play(numbers)

class Ticket:
  def __init__(self, ticket_id, draw_id, plays):
    self.ticket_id = ticket_id
    self.draw_id = draw_id
    self.plays = plays

  def generate(ticket_id, draw_id):
    play1 = Play.generate()
    play2 = Play.generate()
    play3 = Play.generate()
    return Ticket(ticket_id, draw_id, [play1, play2, play3])

class MainDraw:
  def __init__(self, draw_id, rollover, seven_prize_cap, num_maxmillions):
    self.draw_id = draw_id
    self.rollover = rollover
    self.seven_prize_cap = seven_prize_cap

    self.prize_fund = 0
    self.num_maxmillions = num_maxmillions
    self.tickets_by_id = {}

    self.numbers = None
    self.bonus = None
    self.maxmillion_draws = list()
    self.done = False

  def purchase(self):
    self.prize_fund += 2.40
    ticket_id = random.randint(1, 9223372036854775807)
    ticket = Ticket.generate(ticket_id, self.draw_id)
    self.tickets_by_id[ticket.ticket_id] = ticket
    return ticket

  def run(self):
    if self.done:
      raise Error('Draw already done')

    balls = list(range(1, 51))
    random.shuffle(balls)
    self.numbers = set()
    for i in range(8):
      n = balls.pop()
      self.numbers.add(n)
    self.bonus = balls.pop()

    for m in range(self.num_maxmillions):
      max_draw = MaxmillionDraw()
      max_draw.run()
      self.maxmillion_draws.append(max_draw)
    
    self.done = True
    
    print("The draw numbers are ", self.numbers, " and the bonus number is ", self.bonus, ".")
    print("The prize fund is $", self.prize_fund)
  
  def calc_prize_pools(self):
    winners = {}
    winners[PrizeClass.SEVEN] = 0
    winners[PrizeClass.SIX_PLUS] = 0
    winners[PrizeClass.SIX] = 0
    winners[PrizeClass.FIVE_PLUS] = 0
    winners[PrizeClass.FIVE] = 0
    winners[PrizeClass.FOUR_PLUS] = 0
    winners[PrizeClass.FOUR] = 0
    winners[PrizeClass.THREE_PLUS] = 0
    winners[PrizeClass.THREE] = 0

    for ticket_id, ticket in self.tickets_by_id.items():
      for play in ticket.plays:
        matches = set(self.numbers) & set(play.numbers)
        bonus_match = self.bonus in play.numbers

        prize = PrizeClass.for_matches(len(matches), bonus_match)
        if prize is not None:
          winners[prize] += 1

    # Fixed size payouts
    three_payout_size = winners[PrizeClass.THREE] * 2.4
    three_plus_payout_size = winners[PrizeClass.THREE_PLUS] * 20
    four_payout_size = winners[PrizeClass.FOUR] * 20

    total_prize_pool = self.prize_fund - (three_payout_size + three_plus_payout_size + four_payout_size)
    rollover = 0
    prize_pools = {
      PrizeClass.SEVEN: total_prize_pool * 0.8725,
      PrizeClass.SIX_PLUS: total_prize_pool * 0.025,
      PrizeClass.SIX: total_prize_pool * 0.025,
      PrizeClass.FIVE_PLUS: total_prize_pool * 0.015,
      PrizeClass.FIVE: total_prize_pool * 0.035,
      PrizeClass.FOUR_PLUS: total_prize_pool * 0.0275
    }

    if self.rollover > 0:
      prize_pools[PrizeClass.SEVEN] += self.rollover
    maxmillion_pool = 0
    if self.seven_prize_cap is not None and prize_pools[PrizeClass.SEVEN] > self.seven_prize_cap:
      maxmillion_pool += prize_pools[PrizeClass.SEVEN] - self.seven_prize_cap
      prize_pools[PrizeClass.SEVEN] = self.seven_prize_cap

    prize_amounts = {
      PrizeClass.FOUR: 20,
      PrizeClass.THREE_PLUS: 20,
      PrizeClass.THREE: 5
    }
    for prize_class, prize_pool in prize_pools.items():
      winner_count = winners[prize_class]
      if winner_count == 0:
        rollover += prize_pool
        prize_amounts[prize_class] = 0
      else:
        prize_amounts[prize_class] = prize_pool / winner_count

    self.prize_amounts = prize_amounts

    print(winners[PrizeClass.SEVEN], " players matched 7/7. Prize: $", prize_amounts[PrizeClass.SEVEN])
    print(winners[PrizeClass.SIX_PLUS], " players matched 6/7+. Prize: $", prize_amounts[PrizeClass.SIX_PLUS])
    print(winners[PrizeClass.SIX], " players matched 6/7. Prize: $", prize_amounts[PrizeClass.SIX])
    print(winners[PrizeClass.FIVE_PLUS], " players matched 5/7+. Prize: $", prize_amounts[PrizeClass.FIVE_PLUS])
    print(winners[PrizeClass.FIVE], " players matched 5/7. Prize: $", prize_amounts[PrizeClass.FIVE])
    print(winners[PrizeClass.FOUR_PLUS], " players matched 4/7+. Prize: $", prize_amounts[PrizeClass.FOUR_PLUS])
    print(winners[PrizeClass.FOUR], " players matched 4/7. Prize: $", 20)
    print(winners[PrizeClass.THREE_PLUS], " players matched 3/7+. Prize: $", 20)
    print(winners[PrizeClass.THREE], " players matched 3/7. Prize: FREE PLAY ($5 value)")

    for maxmillion_draw in self.maxmillion_draws:
      rollover -= 1000000
      maxmillion_draw.calc_prize_pool(self.tickets_by_id)
      rollover += maxmillion_draw.rollover

    self.rollover = rollover

  def total_prizes(self, ticket):
    if not self.done:
      raise Error('Draw has not run yet.')

    prizes = list()
    for play in ticket.plays:
      matches = set(self.numbers) & set(play.numbers)
      bonus_match = self.bonus in play.numbers

      prize_class = PrizeClass.for_matches(len(matches), bonus_match)
      if prize_class is not None:
        prize = self.prize_amounts[prize_class]
        prizes.append(prize)

      print("The play numbers are ", play.numbers)
      bonus_msg = ""
      if bonus_match:
        bonus_msg = " plus the bonus"
      print(len(matches), "/7 numbers", bonus_msg, " match (", matches, ")")
    print("The prizes are ", prizes)
    return prizes

class MaxmillionDraw:
  def __init__(self):
    self.numbers = None
    self.prize_pool = None
    self.done = False

  def run(self):
    if self.done:
      raise Error('Maxmillion draw already done.')

    balls = set(range(1, 51))
    self.numbers = set()
    while len(self.numbers) < 7:
      self.numbers.add(balls.pop())
    self.done = True

  def calc_prize_pool(self, all_tickets_by_id):
    if not self.done:
      raise Error('Maxmillion draw not done yet.')

    winners = 0

    for ticket_id, ticket in all_tickets_by_id.items():
      for play in ticket.plays:
        matches = self.numbers & play.numbers
        if len(matches) == 7:
          winners += 1

    rollover = 0
    if winners == 0:
      rollover = 1000000
      self.prize_amount = 0
    else:
      self.prize_amount = 1000000 / winners

    self.rollover = rollover

def main():
  draw = MainDraw(1, 101000000, 70000000, 70)
  all_tickets = []
  for i in range(25000000):
    ticket = draw.purchase()
    all_tickets.append(ticket)

    if i % 100000 == 0:
      print("Generated ", i, " tickets.")
  my_ticket = draw.purchase()

  draw.run()
  draw.calc_prize_pools()
  print("Rollover for next draw: $", draw.rollover)

  prizes = draw.total_prizes(my_ticket)
  if len(prizes) > 0:
    print("The ticket has won ", prizes)
  else:
    print("Sorry, not a winner.")

main()
