const fs = require('fs');
const path = require('path');
const { Connection, PublicKey, Keypair, SystemProgram, Transaction, TransactionInstruction, sendAndConfirmTransaction } = require('@solana/web3.js');

const RPC_URL = process.env.RPC_URL || 'https://api.devnet.solana.com';
const PROGRAM_ID = new PublicKey(process.env.GOVERNANCE_PROGRAM_ID || '6amHFyNoPK9MmbBKqthLMeoxTB4TV7CdVE5K4RXi1eDC');

function usage() {
  console.error('Usage: node vote_raw.js <proposal_pubkey> <approve|reject>');
  process.exit(1);
}

async function main(){
  const [proposalArg, decisionArg] = process.argv.slice(2);
  if (!proposalArg || !decisionArg) usage();
  const approve = /^(approve|true|yes|1)$/i.test(decisionArg);

  const connection = new Connection(RPC_URL, 'confirmed');
  const voter = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.config/solana/id.json'), 'utf8')))
  );
  const proposal = new PublicKey(proposalArg);
  const voteRecord = Keypair.generate();

  // Discriminator for "vote" from IDL
  const disc = Buffer.from([227,110,155,23,136,126,172,25]);
  const data = Buffer.concat([disc, Buffer.from([approve ? 1 : 0])]);

  const keys = [
    { pubkey: proposal, isSigner: false, isWritable: true },
    { pubkey: voteRecord.publicKey, isSigner: true, isWritable: true },
    { pubkey: voter.publicKey, isSigner: true, isWritable: true },
    { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
  ];
  const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
  const tx = new Transaction().add(ix);
  const sig = await sendAndConfirmTransaction(connection, tx, [voter, voteRecord], { commitment: 'confirmed' });
  console.log('Vote sent, signature:', sig);
}

main().catch((e) => { console.error(e); process.exit(1); });

