const fs = require('fs');
const path = require('path');
const { Connection, PublicKey, Keypair, SystemProgram, Transaction, TransactionInstruction, sendAndConfirmTransaction } = require('@solana/web3.js');

const RPC_URL = process.env.RPC_URL || 'https://api.devnet.solana.com';
const PROGRAM_ID = new PublicKey(process.env.GOVERNANCE_PROGRAM_ID || '6amHFyNoPK9MmbBKqthLMeoxTB4TV7CdVE5K4RXi1eDC');

function u64ToLE(n){
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(n));
  return buf;
}
function i64ToLE(n){
  const buf = Buffer.alloc(8);
  buf.writeBigInt64LE(BigInt(n));
  return buf;
}
function encodeString(s){
  const b = Buffer.from(s, 'utf8');
  const len = Buffer.alloc(4);
  len.writeUInt32LE(b.length);
  return Buffer.concat([len, b]);
}

function disc(bytes){ return Buffer.from(bytes); }

async function main(){
  const connection = new Connection(RPC_URL, 'confirmed');
  const authority = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.config/solana/id.json'), 'utf8')))
  );

  const idl = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'target', 'idl', 'governance.json'), 'utf8'));
  const discMap = Object.fromEntries(idl.instructions.map(ix => [ix.name, ix.discriminator]));

  // Build initialize ix data
  const initDisc = disc(discMap['initialize']);
  const initData = Buffer.concat([
    initDisc,
    encodeString('MicroAI DAO LLC'),
    encodeString('1621 Central Ave, Cheyenne, WY 82001'),
    encodeString('123 Innovation Drive, Tech City, CA 94000'),
  ]);

  const dao = Keypair.generate();
  const initIx = new TransactionInstruction({
    programId: PROGRAM_ID,
    keys: [
      { pubkey: dao.publicKey, isSigner: true, isWritable: true },
      { pubkey: authority.publicKey, isSigner: true, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data: initData,
  });

  const tx1 = new Transaction().add(initIx);
  console.log('Sending initialize...');
  await sendAndConfirmTransaction(connection, tx1, [authority, dao], { commitment: 'confirmed' });
  console.log('DAO created:', dao.publicKey.toBase58());

  // Create proposal
  const proposal = Keypair.generate();
  const cpDisc = disc(discMap['create_proposal']);
  const cpData = Buffer.concat([
    cpDisc,
    encodeString('Fund Wyoming DAO LLC Registration'),
    encodeString('Allocate funds for legal registration and compliance'),
    u64ToLE(1000),
  ]);

  const cpIx = new TransactionInstruction({
    programId: PROGRAM_ID,
    keys: [
      { pubkey: dao.publicKey, isSigner: false, isWritable: true },
      { pubkey: proposal.publicKey, isSigner: true, isWritable: true },
      { pubkey: authority.publicKey, isSigner: true, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data: cpData,
  });

  const tx2 = new Transaction().add(cpIx);
  console.log('Sending create_proposal...');
  await sendAndConfirmTransaction(connection, tx2, [authority, proposal], { commitment: 'confirmed' });
  console.log('Proposal created:', proposal.publicKey.toBase58());

  fs.writeFileSync(path.join(__dirname, '..', 'onchain-seed.json'), JSON.stringify({
    dao: dao.publicKey.toBase58(),
    proposal: proposal.publicKey.toBase58()
  }, null, 2));
}

main().catch(e => { console.error(e); process.exit(1); });

