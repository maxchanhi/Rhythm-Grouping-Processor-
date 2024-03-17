import random
from fractions import Fraction
import copy

from notation import *

#Generate wrong options
def insert_brackets_randomly(melody_list, num_pairs):
  for _ in range(num_pairs):
    # Ensure there is at least one note between brackets
    left_bracket_pos = random.randint(0, len(melody_list) - 2)  # -2 to
    right_bracket_pos = random.randint(
        left_bracket_pos + 1,
        len(melody_list) -
        1)  # Ensure right bracket comes after the left bracket

    melody_list.insert(left_bracket_pos, "[")  # Insert left bracket
    melody_list.insert(
        right_bracket_pos + 1,
        "]")  # Insert right bracket, +1 due to the left bracket insertion

  return melody_list


#check if the wrong option is correct, regenerate
def check_brackets_at_beats(rhythm_in_melody, melody_with_brackets):

  beat_cutter = []
  beat_jot = [0]

  # Calculate beat positions
  for i in range(len(rhythm_in_melody)):
    beat_cutter.append(durations_fraction[rhythm_in_melody[i]])
    duration_sum = sum(beat_cutter)
    if duration_sum % (1 / 4) == 0:
      beat_jot.append(i + 1)  # +1 because i starts from 0
      beat_cutter.clear()  # Using clear as a method

  beat_jot.append(len(rhythm_in_melody) + 1)

  # Find bracket positions
  opening_brackets = [
      i for i, x in enumerate(melody_with_brackets) if x == "["
  ]
  closing_brackets = [
      i for i, x in enumerate(melody_with_brackets) if x == "]"
  ]

  # Check if any brackets are at the main beats
  for bracket_pos in opening_brackets + closing_brackets:
    if bracket_pos in beat_jot:
      return False

  return True


# For correct answer


def combine_rest(perBar):
  check_chars = "abcdefg"
  rest_list = [2, 4, 8, 16]

  for rest_check in rest_list:
    position_list = [0]
    sum_rest = 0
    position = 0
    correct = []
    print("perBar", perBar, "rest_check", rest_check)
    for note in perBar:
      sum_rest += note[1]
      position += 1
      if sum_rest % Fraction(1, rest_check) == 0:
        position_list.append(position)
        sum_rest = 0

    idx = 0
    while idx < (len(position_list) - 1):
      count = 0
      current_sublist = perBar[position_list[idx]:position_list[idx + 1]]
      for note in current_sublist:
        if any(char in note[0] for char in check_chars):
          count += 1

      if count != 0:
        correct.extend(current_sublist)
      elif count == 0 and len(current_sublist) > 1:
        correct.append([f"r{rest_check}", Fraction(1, rest_check)])
      elif count == 0 and len(current_sublist) == 1:
        correct.extend(current_sublist)

      idx += 1
    perBar = correct

  return perBar


def change_note_based_on_fraction(note, tie=False):
  lily, fraction = note
  if '.' in lily:
    lily = lily.replace('.', '')
    rhythm_value = int(fraction.denominator)

    pitch, octave = lily.split("'")
    if tie == False:
      lily = pitch + "'" + str(rhythm_value)
    elif tie == True:
      lily = pitch + "'" + str(rhythm_value) + "~"
  else:
    pass
  return [lily, fraction]


# fix note group but not rest
def seperate_note(note_to_change, stnew_note, nd_note):
  pitch, _ = note_to_change
  st_new_rhythm = fraction_to_lilypond[stnew_note]
  nd_new_rhythm = fraction_to_lilypond[nd_note]
  pitch = pitch.split("'")[0]
  return [[pitch + "'" + st_new_rhythm + "~", stnew_note],
          [pitch + "'" + nd_new_rhythm, nd_note]]
def change_note(note_to_change, new_duration):
  pitch, octave = note_to_change[0].split("'")
  rhythm_value = int( Fraction(1,new_duration))
  return [pitch+"'"+str(rhythm_value),new_duration]


def beat_cutter(melody, check, session=0):
  main_beat = []
  value = beat_p = 0
  for note in melody:
    value += note[1]
    if value == Fraction(1, check) or note[1]>=Fraction(1, check):
      value = 0
    if value > Fraction(1, check):
      main_beat.append([beat_p, value])
      value = 0
    beat_p += 1
    if len(main_beat) == 1:
      break
  if main_beat:
    beat_pos,beat_value = main_beat[0]
    ex_beat = beat_value - Fraction(1, check)
    in_beat = melody[beat_pos][1] - ex_beat
    if ex_beat and in_beat:
      melody[beat_pos:beat_pos + 1] = seperate_note(melody[beat_pos], in_beat,ex_beat)
      
  if session < len(melody) // 4:
    return beat_cutter(melody, check, session + 1)
  return melody


def main_grouping(melody,uppertime, lowertime):
  if uppertime == 3 or uppertime == 9:
    rhythm_checklist = [lowertime]
  else:
    rhythm_checklist = [lowertime // 2, lowertime]
  for check_value in rhythm_checklist:
    melody = beat_cutter(melody, check_value)
    print(melody)
  return melody

import re
#fix rest
def extract_duration_digit(note_string):

    match = re.search(r'\d+', note_string)
    if match:
        return int(match.group())
    else:
        raise ValueError("No duration digit found in the string.")
def change_rest( stnote, nd_note):
  st_new_rhythm = fraction_to_lilypond[stnote]
  nd_new_rhythm = fraction_to_lilypond[nd_note]
  rest = "r"
  return [[rest + st_new_rhythm ,stnote],
          [rest + nd_new_rhythm,nd_note]]


def rest_beat_cutter(melody, check, session=0):
  main_beat = []
  value = 0
  beat_p = 0
  changed = False
  for note in melody:
    value += note[1]
    if value >= Fraction(1, check) :
      if "r" in note[0]:
        main_beat.append([beat_p, value])
      value = 0
    beat_p += 1
  print("main_beat", main_beat)
  for beat in main_beat:
    if  melody[beat[0]][1] >= Fraction(1, check):
      ex_beat = beat[1] - Fraction(1, check)
      in_beat = melody[beat[0]][1] - ex_beat
      if ex_beat and in_beat:

        melody[beat[0]:beat[0] + 1] = change_rest(in_beat, ex_beat)

  if session < int(len(melody) / 4):
    return rest_beat_cutter(melody, check=check, session=session + 1)
  else:
    return melody,changed

def main_restgrouping(melody, lowertime):
  rhythm_checklist = []
  for note in melody:
    if "r" in note[0]:
      c_value = extract_duration_digit(note[0])
      rhythm_checklist.append(c_value)
  rhythm_checklist.sort()
  for check_value in rhythm_checklist:
    melody,changed = rest_beat_cutter(melody, check_value)

  return melody


