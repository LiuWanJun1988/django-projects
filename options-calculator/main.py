#! /usr/bin/env python
from calculators import basic, spreads, advanced, custom


def main():
    print('Please choose an option calculator from the following options: \n')
    print('1 - Basic')
    print('2 - Spreads')
    print('3 - Advanced')
    print('4 - Custom\n')
    calculator = input('Calculator: ')

    print('\nPlease select an option strategy: \n')

    try:
        # BASIC
        if calculator == '1':
            basic.run()

        # SPREADS
        elif calculator == '2':
            spreads.run()

        # ADVANCED
        elif calculator == '3':
            advanced.run()

        elif calculator == '4':
            custom.run()
    except:
        print('Please choose a valid calculator.')


if __name__ == '__main__':
    main()