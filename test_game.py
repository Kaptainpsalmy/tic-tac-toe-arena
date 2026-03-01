import requests
import json
import time
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()


class TicTacToeTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }

    def print_test_result(self, test_name, success, expected=None, got=None):
        """Print colored test result"""
        self.test_results['total'] += 1
        if success:
            self.test_results['passed'] += 1
            print(f"{Fore.GREEN}✓ PASS: {test_name}{Style.RESET_ALL}")
        else:
            self.test_results['failed'] += 1
            print(f"{Fore.RED}✗ FAIL: {test_name}{Style.RESET_ALL}")
            if expected and got:
                print(f"  Expected: {expected}")
                print(f"  Got: {got}")

    def test_health(self):
        """Test health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.print_test_result("Health check", success)
            return success
        except Exception as e:
            self.print_test_result("Health check", False, error=str(e))
            return False

    def test_new_game(self):
        """Test new game creation"""
        response = self.session.post(f"{self.base_url}/api/new-game")
        data = response.json()

        success = (response.status_code == 200 and
                   data['success'] and
                   all(cell == '' for cell in data['game_state']['board']))

        self.print_test_result("New game creation", success)
        return success

    def test_valid_move(self):
        """Test making a valid move"""
        # Start fresh
        self.session.post(f"{self.base_url}/api/new-game")

        # Make move at center
        response = self.session.post(
            f"{self.base_url}/api/move",
            json={"position": 4}
        )
        data = response.json()

        success = (response.status_code == 200 and
                   data['success'] and
                   data['game_state']['board'][4] == 'X' and
                   data['game_state']['current_player'] == 'O')

        self.print_test_result("Valid move", success)
        return success

    def test_invalid_move_out_of_bounds(self):
        """Test invalid move (position out of bounds)"""
        self.session.post(f"{self.base_url}/api/new-game")

        response = self.session.post(
            f"{self.base_url}/api/move",
            json={"position": 9}
        )
        data = response.json()

        success = (response.status_code == 200 and
                   not data['success'] and
                   'out of range' in data['message'].lower())

        self.print_test_result("Invalid move (out of bounds)", success)
        return success

    def test_invalid_move_taken(self):
        """Test invalid move (position already taken)"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Make first move
        self.session.post(f"{self.base_url}/api/move", json={"position": 4})

        # Try to make move at same position
        response = self.session.post(
            f"{self.base_url}/api/move",
            json={"position": 4}
        )
        data = response.json()

        success = (response.status_code == 200 and
                   not data['success'] and
                   'already taken' in data['message'].lower())

        self.print_test_result("Invalid move (position taken)", success)
        return success

    def test_win_condition_row(self):
        """Test win condition - top row"""
        self.session.post(f"{self.base_url}/api/new-game")

        # X moves to win top row
        moves = [0, 3, 1, 4, 2]  # X: 0,1,2 (top row)
        for pos in moves:
            self.session.post(f"{self.base_url}/api/move", json={"position": pos})

        response = self.session.get(f"{self.base_url}/api/game-state")
        data = response.json()

        success = (data['game_state']['winner'] == 'X' and
                   data['game_state']['game_over'])

        self.print_test_result("Win condition - row", success)
        return success

    def test_win_condition_column(self):
        """Test win condition - first column"""
        self.session.post(f"{self.base_url}/api/new-game")

        # X moves to win first column
        moves = [0, 1, 3, 2, 6]  # X: 0,3,6 (first column)
        for pos in moves:
            self.session.post(f"{self.base_url}/api/move", json={"position": pos})

        response = self.session.get(f"{self.base_url}/api/game-state")
        data = response.json()

        success = (data['game_state']['winner'] == 'X' and
                   data['game_state']['game_over'])

        self.print_test_result("Win condition - column", success)
        return success

    def test_win_condition_diagonal(self):
        """Test win condition - diagonal"""
        self.session.post(f"{self.base_url}/api/new-game")

        # X moves to win main diagonal
        moves = [0, 1, 4, 2, 8]  # X: 0,4,8 (diagonal)
        for pos in moves:
            self.session.post(f"{self.base_url}/api/move", json={"position": pos})

        response = self.session.get(f"{self.base_url}/api/game-state")
        data = response.json()

        success = (data['game_state']['winner'] == 'X' and
                   data['game_state']['game_over'])

        self.print_test_result("Win condition - diagonal", success)
        return success

    def test_draw_condition(self):
        """Test draw condition"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Play a draw game
        moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]
        for pos in moves:
            self.session.post(f"{self.base_url}/api/move", json={"position": pos})

        response = self.session.get(f"{self.base_url}/api/game-state")
        data = response.json()

        success = (data['game_state']['winner'] is None and
                   data['game_state']['game_over'] and
                   all(cell != '' for cell in data['game_state']['board']))

        self.print_test_result("Draw condition", success)
        return success

    def test_game_over_prevents_moves(self):
        """Test that moves are prevented after game over"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Create win
        moves = [0, 3, 1, 4, 2]
        for pos in moves:
            self.session.post(f"{self.base_url}/api/move", json={"position": pos})

        # Try to make another move
        response = self.session.post(
            f"{self.base_url}/api/move",
            json={"position": 5}
        )
        data = response.json()

        success = (not data['success'] and
                   'already over' in data['message'].lower())

        self.print_test_result("Prevent moves after game over", success)
        return success

    def test_reset_game(self):
        """Test reset game functionality"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Make some moves
        self.session.post(f"{self.base_url}/api/move", json={"position": 4})
        self.session.post(f"{self.base_url}/api/move", json={"position": 0})

        # Reset
        response = self.session.post(f"{self.base_url}/api/reset")
        data = response.json()

        success = (response.status_code == 200 and
                   data['success'] and
                   all(cell == '' for cell in data['game_state']['board']) and
                   data['game_state']['current_player'] == 'X')

        self.print_test_result("Reset game", success)
        return success

    def test_valid_moves_endpoint(self):
        """Test valid moves endpoint"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Make a move
        self.session.post(f"{self.base_url}/api/move", json={"position": 4})

        # Get valid moves
        response = self.session.get(f"{self.base_url}/api/valid-moves")
        data = response.json()

        success = (response.status_code == 200 and
                   data['success'] and
                   len(data['valid_moves']) == 8 and
                   4 not in data['valid_moves'])

        self.print_test_result("Valid moves endpoint", success)
        return success

    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Make some moves
        self.session.post(f"{self.base_url}/api/move", json={"position": 4})
        self.session.post(f"{self.base_url}/api/move", json={"position": 0})

        # Get statistics
        response = self.session.get(f"{self.base_url}/api/statistics")
        data = response.json()

        success = (response.status_code == 200 and
                   data['success'] and
                   data['statistics']['total_moves'] == 2)

        self.print_test_result("Statistics endpoint", success)
        return success

    def test_validate_position_endpoint(self):
        """Test validate position endpoint"""
        self.session.post(f"{self.base_url}/api/new-game")

        # Test valid position
        response = self.session.post(
            f"{self.base_url}/api/validate-position",
            json={"position": 4}
        )
        data = response.json()

        success = data['valid']

        self.print_test_result("Validate position - valid", success)

        # Make a move
        self.session.post(f"{self.base_url}/api/move", json={"position": 4})

        # Test invalid position
        response = self.session.post(
            f"{self.base_url}/api/validate-position",
            json={"position": 4}
        )
        data = response.json()

        success = not data['valid']

        self.print_test_result("Validate position - taken", success)
        return success

    def run_all_tests(self):
        """Run all tests"""
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Running Tic Tac Toe Test Suite{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

        # Check if server is running
        if not self.test_health():
            print(f"{Fore.RED}❌ Server not responding. Make sure Flask is running on {self.base_url}{Style.RESET_ALL}")
            return

        # Run all tests
        tests = [
            self.test_new_game,
            self.test_valid_move,
            self.test_invalid_move_out_of_bounds,
            self.test_invalid_move_taken,
            self.test_win_condition_row,
            self.test_win_condition_column,
            self.test_win_condition_diagonal,
            self.test_draw_condition,
            self.test_game_over_prevents_moves,
            self.test_reset_game,
            self.test_valid_moves_endpoint,
            self.test_statistics_endpoint,
            self.test_validate_position_endpoint
        ]

        for test in tests:
            test()
            time.sleep(0.1)  # Small delay between tests

        # Print summary
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Test Summary{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"Total tests: {self.test_results['total']}")
        print(f"{Fore.GREEN}Passed: {self.test_results['passed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.test_results['failed']}{Style.RESET_ALL}")

        if self.test_results['failed'] == 0:
            print(f"\n{Fore.GREEN}✅ ALL TESTS PASSED! Game is ready for production!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Some tests failed. Review the issues above.{Style.RESET_ALL}")


if __name__ == "__main__":
    # Install colorama if not present: pip install colorama
    tester = TicTacToeTester()
    tester.run_all_tests()