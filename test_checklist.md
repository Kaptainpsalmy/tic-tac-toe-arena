# 🎮 Tic Tac Toe - Manual Testing Checklist

## Game Initialization
- [ ] Game loads with empty board
- [ ] Status shows "Player X's turn"
- [ ] Reset button is enabled
- [ ] Undo button is disabled initially

## Move Validation
- [ ] Clicking empty cell places X
- [ ] Turn switches to O after X moves
- [ ] Clicking same cell twice doesn't change
- [ ] Cannot move after game over
- [ ] Error message appears for invalid moves

## Win Conditions
- [ ] Top row win (positions 0,1,2)
- [ ] Middle row win (3,4,5)
- [ ] Bottom row win (6,7,8)
- [ ] First column win (0,3,6)
- [ ] Second column win (1,4,7)
- [ ] Third column win (2,5,8)
- [ ] Main diagonal win (0,4,8)
- [ ] Anti-diagonal win (2,4,6)

## Win Effects
- [ ] Winning line highlights
- [ ] Confetti appears
- [ ] Winning overlay shows
- [ ] Winner's score increments
- [ ] Sound plays (if enabled)

## Draw Condition
- [ ] Full board with no winner shows draw
- [ ] Draw message appears
- [ ] No score increment
- [ ] Draw sound plays

## Game Controls
- [ ] Reset button clears board
- [ ] Undo button reverts last move
- [ ] Settings modal opens/closes
- [ ] Sound toggle works
- [ ] Theme toggle works
- [ ] Keyboard shortcuts (R, U, ESC)

## Move History
- [ ] Moves appear in history panel
- [ ] X and O moves color-coded
- [ ] Clear history button works
- [ ] History persists after page refresh

## Responsive Design
- [ ] Desktop view (1200px+)
- [ ] Tablet view (768px - 1199px)
- [ ] Mobile view (<768px)
- [ ] Touch interactions work
- [ ] No horizontal scroll

## Performance
- [ ] No console errors
- [ ] Smooth animations (60fps)
- [ ] Fast API responses (<200ms)
- [ ] Memory usage stable

## Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Edge Cases
- [ ] Rapid clicking doesn't break game
- [ ] Page refresh maintains state
- [ ] Multiple tabs maintain separate games
- [ ] Server restart recovers gracefully
- [ ] Invalid JSON in API returns 400
- [ ] Missing session creates new game