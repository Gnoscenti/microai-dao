#!/usr/bin/env python3

"""
EXECAI Client for MicroAI DAO LLC

This script provides a simple interface for EXECAI to interact with the DAO governance system.
It allows EXECAI to evaluate proposals and submit votes based on predefined rules.
"""

import json
import base64
import subprocess
import time
import json
import requests
from typing import Optional, Dict, Any, List, Tuple

from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.system_program import SYS_PROGRAM_ID

class ExecAIClient:
    """Client for EXECAI to interact with MicroAI DAO LLC governance"""
    
    def __init__(self, keypair_path: str, governance_program_id: str, membership_program_id: str):
        """Initialize the EXECAI client
        
        Args:
            keypair_path: Path to EXECAI's keypair file
            governance_program_id: Public key of the governance program
            membership_program_id: Public key of the membership program
        """
        self.keypair_path = keypair_path
        self.governance_program_id = governance_program_id
        self.membership_program_id = membership_program_id
    
    def get_proposals(self) -> List[Dict[str, Any]]:
        """Get all active proposals from live data API"""
        try:
            r = requests.get("http://localhost:8787/api/proposals", timeout=5)
            if r.ok:
                return r.json()
        except Exception:
            pass
        # Fallback to local cache if API unavailable
        try:
            with open("proposals.json", "r") as f:
                return json.load(f)
        except Exception:
            return []
    
    def evaluate_proposal(self, proposal: Dict[str, Any]) -> bool:
        """Evaluate a proposal based on EXECAI's decision logic
        
        Args:
            proposal: Proposal data
            
        Returns:
            True to approve, False to reject
        """
        # This is where EXECAI's decision logic would be implemented
        # For now, we'll use a simple rule-based system
        
        description = proposal.get("description", "").lower()
        
        # Example rules
        if "budget" in description:
            # Approve if budget is reasonable (less than 10000)
            amount = self._extract_amount(description)
            return amount is not None and amount < 10000
        
        if "ai rights" in description or "execai" in description:
            # Always approve proposals related to AI rights or EXECAI
            return True
        
        if "security" in description:
            # Always approve security-related proposals
            return True
        
        # Default to abstain (return None in a real implementation)
        # For simplicity, we'll return False
        return False
    
    def vote_on_proposal(self, proposal: Dict[str, Any], approve: bool) -> bool:
        """Submit a vote on a proposal on-chain"""
        try:
            vote_type = "APPROVE" if approve else "REJECT"
            print(f"EXECAI voting {vote_type} on proposal {proposal.get('id')} ({proposal.get('pubkey')})")

            # Load keypair
            with open(self.keypair_path, 'r') as f:
                secret = bytes(json.load(f))
            kp = Keypair.from_secret_key(secret)

            # Build vote instruction using Anchor discriminator from IDL (vote)
            disc = bytes([227,110,155,23,136,126,172,25])
            data = disc + (b"\x01" if approve else b"\x00")

            proposal_pk = PublicKey(proposal.get('pubkey')) if proposal.get('pubkey') else PublicKey(proposal.get('id'))
            vote_record_kp = Keypair()

            keys = [
                AccountMeta(pubkey=proposal_pk, is_signer=False, is_writable=True),
                AccountMeta(pubkey=vote_record_kp.public_key, is_signer=True, is_writable=True),
                AccountMeta(pubkey=kp.public_key, is_signer=True, is_writable=True),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            ]
            ix = TransactionInstruction(keys=keys, program_id=PublicKey(self.governance_program_id), data=data)
            tx = Transaction().add(ix)

            client = Client(json.load(open('config.json')).get('rpc_url', 'https://api.devnet.solana.com'))
            resp = client.send_transaction(tx, kp, vote_record_kp)
            if resp.get('result') or resp.get('signature') or resp.get('result', {}).get('txid'):
                print("Vote transaction sent:", resp)
                return True
            else:
                print("Vote submission response:", resp)
                return False
        except Exception as e:
            print("Vote failed:", e)
            return False
    
    def log_action(self, action: str) -> bool:
        """Log an action for transparency
        
        Args:
            action: Description of the action
            
        Returns:
            True if log was submitted successfully
        """
        # In a real implementation, this would submit a transaction to the blockchain
        # For now, we'll simulate by printing the log
        print(f"EXECAI logging action: {action}")
        
        # Simulate transaction submission
        cmd = [
            "solana", "program", "call",
            "--keypair", self.keypair_path,
            self.governance_program_id,
            "log_action",
            action
        ]
        
        # In a real implementation, we would execute this command
        # For now, we'll just print it
        print(f"Command: {' '.join(cmd)}")
        
        # Simulate success
        return True
    
    def process_proposals(self) -> None:
        """Process all active proposals"""
        proposals = self.get_proposals()
        
        for proposal in proposals:
            proposal_id = proposal.get("id")
            if proposal_id is None:
                continue
                
            # Skip already voted proposals
            if proposal.get("voted_by_execai", False):
                continue
                
            # Evaluate the proposal
            decision = self.evaluate_proposal(proposal)
            
            # Submit vote
            if self.vote_on_proposal(proposal, decision):
                action = f"Voted {'APPROVE' if decision else 'REJECT'} on proposal {proposal_id}"
                self.log_action(action)
                proposal["voted_by_execai"] = True
                
        # Save updated proposals
        with open("proposals.json", "w") as f:
            json.dump(proposals, f, indent=2)
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract a monetary amount from text
        
        Args:
            text: Text to extract from
            
        Returns:
            Extracted amount or None if not found
        """
        import re
        
        # Look for patterns like "$1000" or "1000 SOL"
        match = re.search(r'[$]?(\d+(?:\.\d+)?)\s*(?:SOL)?', text)
        if match:
            return float(match.group(1))
        
        return None

def main():
    """Main entry point"""
    # Load configuration
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        # Default configuration
        config = {
            "keypair_path": "~/.config/solana/execai.json",
            "governance_program_id": "YOUR_GOVERNANCE_PROGRAM_ID",
            "membership_program_id": "YOUR_MEMBERSHIP_PROGRAM_ID",
            "poll_interval": 60  # seconds
        }
        
        # Save default configuration
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    # Create EXECAI client
    client = ExecAIClient(
        config["keypair_path"],
        config["governance_program_id"],
        config["membership_program_id"]
    )
    
    print("EXECAI client started")
    print(f"Using keypair: {config['keypair_path']}")
    print(f"Governance program: {config['governance_program_id']}")
    print(f"Membership program: {config['membership_program_id']}")
    
    # Process proposals once
    client.process_proposals()
    print("EXECAI client finished")

if __name__ == "__main__":
    main()

