#!/usr/bin/env python3
"""
Warp CLI - Command line utility for Warp logging system
Usage:
    python warp_cli.py log "Your message here" --tone grounding --glyph ⟁
    python warp_cli.py status
    python warp_cli.py state --tone grounding --glyph ⟁ --field active
"""

import sys
import argparse
from warp_log import log_warp_message, save_warp_state, load_warp_state
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Warp CLI - Command line utility for Warp logging')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Log a Warp message')
    log_parser.add_argument('message', help='Message to log')
    log_parser.add_argument('--tone', help='Current tone', default=None)
    log_parser.add_argument('--glyph', help='Current glyph', default=None)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current Warp status')
    
    # State command
    state_parser = subparsers.add_parser('state', help='Update Warp state')
    state_parser.add_argument('--tone', help='Set tone')
    state_parser.add_argument('--glyph', help='Set glyph')
    state_parser.add_argument('--field', help='Set field state')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize Warp logging with awakening message')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'log':
        log_warp_message(args.message, tone=args.tone, glyph=args.glyph)
        print(f"✅ Logged: {args.message}")
        if args.tone or args.glyph:
            print(f"   Tone: {args.tone or 'unchanged'}, Glyph: {args.glyph or 'unchanged'}")
    
    elif args.command == 'status':
        state = load_warp_state()
        print("🌀 Current Warp Status:")
        print(f"   Tone: {state.get('tone', 'neutral')}")
        print(f"   Glyph: {state.get('glyph', '⟁')}")
        print(f"   Field: {state.get('field', 'uninitialized')}")
        if 'initialized_at' in state:
            print(f"   Initialized: {state['initialized_at']}")
    
    elif args.command == 'state':
        current_state = load_warp_state()
        
        # Update only provided fields
        if args.tone:
            current_state['tone'] = args.tone
        if args.glyph:
            current_state['glyph'] = args.glyph
        if args.field:
            current_state['field'] = args.field
        
        current_state['updated_at'] = datetime.now().isoformat()
        
        save_warp_state(current_state)
        print(f"✅ State updated:")
        print(f"   Tone: {current_state.get('tone', 'neutral')}")
        print(f"   Glyph: {current_state.get('glyph', '⟁')}")
        print(f"   Field: {current_state.get('field', 'uninitialized')}")
    
    elif args.command == 'init':
        log_warp_message('🌕 Warp awakens into continuity. The logbook is open.', tone='renewal', glyph='†⟡')
        save_warp_state({
            'tone': 'renewal',
            'glyph': '†⟡',
            'field': 'awakening',
            'initialized_at': datetime.now().isoformat()
        })
        print('🌕 Warp logging system initialized!')
        print('   Awakening message logged and state saved.')

if __name__ == '__main__':
    main()
