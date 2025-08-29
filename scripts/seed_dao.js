const fs = require('fs');
const path = require('path');
const anchor = require('@project-serum/anchor');
const { Connection, PublicKey, Keypair, SystemProgram, LAMPORTS_PER_SOL } = require('@solana/web3.js');

const RPC_URL = process.env.RPC_URL || 'https://api.devnet.solana.com';
const PROGRAM_ID = new PublicKey(process.env.GOVERNANCE_PROGRAM_ID || '52PRY4415Rx29Za61422XJHUoUbs5ysqW5eZtksTTX8d');

async function main(){
  const connection = new Connection(RPC_URL, 'confirmed');
  const walletKeypair = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.config/solana/id.json'), 'utf8')))
  );
  const wallet = new anchor.Wallet(walletKeypair);
  const provider = new anchor.AnchorProvider(connection, wallet, { commitment: 'confirmed', preflightCommitment: 'confirmed' });
  anchor.setProvider(provider);

  const idl = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'target', 'idl', 'governance.json'), 'utf8'));
  const program = new anchor.Program(idl, PROGRAM_ID, provider);

  // Airdrop if needed
  const bal = await connection.getBalance(wallet.publicKey);
  if (bal < 0.5 * LAMPORTS_PER_SOL){
    await connection.requestAirdrop(wallet.publicKey, 2 * LAMPORTS_PER_SOL);
  }

  // Create DAO
  const dao = Keypair.generate();
  console.log('Initializing DAO:', dao.publicKey.toBase58());
  await program.methods.initialize(
    'MicroAI DAO LLC',
    '1621 Central Ave, Cheyenne, WY 82001',
    '123 Innovation Drive, Tech City, CA 94000'
  ).accounts({
    dao: dao.publicKey,
    authority: wallet.publicKey,
    systemProgram: SystemProgram.programId
  }).signers([dao]).rpc();

  // Create a proposal
  const proposal = Keypair.generate();
  console.log('Creating proposal:', proposal.publicKey.toBase58());
  await program.methods.createProposal(
    'Fund Wyoming DAO LLC Registration',
    'Allocate funds for legal registration and compliance',
    new anchor.BN(1000)
  ).accounts({
    dao: dao.publicKey,
    proposal: proposal.publicKey,
    proposer: wallet.publicKey,
    systemProgram: SystemProgram.programId
  }).signers([proposal]).rpc();

  fs.writeFileSync(path.join(__dirname, '..', 'onchain-seed.json'), JSON.stringify({
    dao: dao.publicKey.toBase58(),
    proposal: proposal.publicKey.toBase58()
  }, null, 2));

  console.log('Seed complete');
}

main().catch((e) => { console.error(e); process.exit(1); });

