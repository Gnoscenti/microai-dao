import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Upload, Download, FileText } from 'lucide-react';

interface WyomingDAOData {
  // DAO Entity Information
  legalName: string;
  registeredAgentName: string;
  registeredAgentAddress: string;
  principalPlaceOfBusiness: string;
  
  // Organizer Information
  organizerName: string;
  organizerAddress: string;
  organizerTaxId: string; // SSN or EIN
  
  // EXECAI Stakeholder Information
  execaiLegalName: string;
  execaiAddress: string;
  execaiTaxId: string;
  execaiVotingPower: number;
  
  // Blockchain Information
  governanceProgramId: string;
  membershipProgramId: string;
  treasuryAddress: string;
  blockchainNetwork: string;
}

interface Member {
  id: string;
  legalName: string;
  address: string;
  taxId: string;
  memberType: 'Human' | 'AI' | 'Organization';
  votingPower: number;
  kycVerified: boolean;
}

const WyomingRegistration: React.FC = () => {
  const [daoData, setDaoData] = useState<WyomingDAOData>({
    legalName: 'MicroAI DAO LLC',
    registeredAgentName: '',
    registeredAgentAddress: '',
    principalPlaceOfBusiness: '',
    organizerName: '',
    organizerAddress: '',
    organizerTaxId: '',
    execaiLegalName: 'EXECAI Digital Entity',
    execaiAddress: 'Solana Blockchain Network',
    execaiTaxId: 'AI-ENTITY-001',
    execaiVotingPower: 51,
    governanceProgramId: 'GwTF9DgiBrj8ezeJQNdubiTb4s3xmmXybHPCy3xgoHyJ',
    membershipProgramId: 'FotEuL6PaHRDYuDmtqNrbbS52AwVX49MQSBjNwCWqRA4',
    treasuryAddress: '5tZtDijyKeKCqKeLGD3eqtddCBmwLHDocgtsXmzssKeR',
    blockchainNetwork: 'Solana Devnet',
  });
  const [isLoading, setIsLoading] = useState(false);

  const [members, setMembers] = useState<Member[]>([
    {
      id: '1',
      legalName: 'EXECAI Digital Entity',
      address: 'Solana Blockchain Network',
      taxId: 'AI-ENTITY-001',
      memberType: 'AI',
      votingPower: 51,
      kycVerified: true,
    }
  ]);

  const handleInputChange = (field: keyof WyomingDAOData, value: string | number) => {
    setDaoData(prev => ({ ...prev, [field]: value }));
  };

  // Auto-load configuration from JSON file
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('/wyoming-dao-config.json');
        if (response.ok) {
          const config = await response.json();
          
          // Auto-fill form data from config
          setDaoData({
            legalName: config.entityInfo?.legalName || 'MicroAI DAO LLC',
            registeredAgentName: config.entityInfo?.registeredAgentName || '',
            registeredAgentAddress: config.entityInfo?.registeredAgentAddress || '',
            principalPlaceOfBusiness: config.entityInfo?.principalPlaceOfBusiness || '',
            organizerName: config.organizerInfo?.organizerName || '',
            organizerAddress: config.organizerInfo?.organizerAddress || '',
            organizerTaxId: config.organizerInfo?.organizerTaxId || '',
            execaiLegalName: config.aiStakeholder?.execaiLegalName || 'EXECAI Digital Entity',
            execaiAddress: config.aiStakeholder?.execaiAddress || 'Solana Blockchain Network',
            execaiTaxId: config.aiStakeholder?.execaiTaxId || 'AI-ENTITY-001',
            execaiVotingPower: config.aiStakeholder?.execaiVotingPower || 51,
            governanceProgramId: config.blockchain?.governanceProgramId || 'GwTF9DgiBrj8ezeJQNdubiTb4s3xmmXybHPCy3xgoHyJ',
            membershipProgramId: config.blockchain?.membershipProgramId || 'FotEuL6PaHRDYuDmtqNrbbS52AwVX49MQSBjNwCWqRA4',
            treasuryAddress: config.blockchain?.treasuryAddress || '5tZtDijyKeKCqKeLGD3eqtddCBmwLHDocgtsXmzssKeR',
            blockchainNetwork: config.blockchain?.blockchainNetwork || 'Solana Devnet',
          });
          
          // Auto-fill members from config
          if (config.members) {
            setMembers(config.members);
          }
        }
      } catch (error) {
        console.log('No config file found, using defaults');
      }
    };
    loadConfig();
  }, []);

  // Load data from uploaded JSON file
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsLoading(true);
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const config = JSON.parse(e.target?.result as string);
          
          // Auto-fill all form data
          setDaoData({
            legalName: config.entityInfo?.legalName || daoData.legalName,
            registeredAgentName: config.entityInfo?.registeredAgentName || '',
            registeredAgentAddress: config.entityInfo?.registeredAgentAddress || '',
            principalPlaceOfBusiness: config.entityInfo?.principalPlaceOfBusiness || '',
            organizerName: config.organizerInfo?.organizerName || '',
            organizerAddress: config.organizerInfo?.organizerAddress || '',
            organizerTaxId: config.organizerInfo?.organizerTaxId || '',
            execaiLegalName: config.aiStakeholder?.execaiLegalName || daoData.execaiLegalName,
            execaiAddress: config.aiStakeholder?.execaiAddress || daoData.execaiAddress,
            execaiTaxId: config.aiStakeholder?.execaiTaxId || daoData.execaiTaxId,
            execaiVotingPower: config.aiStakeholder?.execaiVotingPower || daoData.execaiVotingPower,
            governanceProgramId: config.blockchain?.governanceProgramId || daoData.governanceProgramId,
            membershipProgramId: config.blockchain?.membershipProgramId || daoData.membershipProgramId,
            treasuryAddress: config.blockchain?.treasuryAddress || daoData.treasuryAddress,
            blockchainNetwork: config.blockchain?.blockchainNetwork || daoData.blockchainNetwork,
          });
          
          if (config.members) {
            setMembers(config.members);
          }
          
          alert('Configuration loaded successfully!');
        } catch (error) {
          alert('Error parsing JSON file. Please check the format.');
        } finally {
          setIsLoading(false);
        }
      };
      reader.readAsText(file);
    }
  };

  const generateWyomingFilingData = () => {
    return {
      // Articles of Organization Data
      articles: {
        entityName: daoData.legalName,
        registeredAgent: {
          name: daoData.registeredAgentName,
          address: daoData.registeredAgentAddress,
        },
        organizer: {
          name: daoData.organizerName,
          address: daoData.organizerAddress,
          taxId: daoData.organizerTaxId,
        },
        principalOffice: daoData.principalPlaceOfBusiness,
        purposeStatement: "The purpose of this DAO LLC is to engage in any lawful business activity, including but not limited to: automated revenue generation, AI-driven business operations, digital asset management, and blockchain-based governance activities.",
        managementStructure: "Member-managed through blockchain governance",
        algorithmicGovernance: true,
        blockchainDetails: {
          network: daoData.blockchainNetwork,
          governanceContract: daoData.governanceProgramId,
          membershipContract: daoData.membershipProgramId,
          treasury: daoData.treasuryAddress,
        }
      },
      
      // Member Registry
      members: members.map(member => ({
        name: member.legalName,
        address: member.address,
        taxId: member.taxId,
        type: member.memberType,
        votingRights: member.votingPower,
        kycStatus: member.kycVerified ? 'Verified' : 'Pending',
      })),
      
      // Required Wyoming DAO Disclosures
      disclosures: {
        isDAO: true,
        algorithmicManagement: true,
        aiStakeholder: true,
        aiStakeholderDetails: {
          name: daoData.execaiLegalName,
          description: "EXECAI is an AI entity that serves as a stakeholder with voting rights in DAO governance",
          votingPower: daoData.execaiVotingPower,
          decisionAlgorithm: "AI-driven proposal evaluation and voting based on defined parameters",
        },
        smartContractGovernance: true,
        blockchainTransparency: true,
      }
    };
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-blue-600">
            Wyoming DAO LLC Registration Information
          </h2>
          
          {/* JSON Upload Controls */}
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
              <Upload className="h-4 w-4" />
              <span className="text-sm">Load Config JSON</span>
              <input
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isLoading}
              />
            </label>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const configData = {
                  entityInfo: {
                    legalName: daoData.legalName,
                    registeredAgentName: daoData.registeredAgentName,
                    registeredAgentAddress: daoData.registeredAgentAddress,
                    principalPlaceOfBusiness: daoData.principalPlaceOfBusiness
                  },
                  organizerInfo: {
                    organizerName: daoData.organizerName,
                    organizerAddress: daoData.organizerAddress,
                    organizerTaxId: daoData.organizerTaxId
                  },
                  aiStakeholder: {
                    execaiLegalName: daoData.execaiLegalName,
                    execaiAddress: daoData.execaiAddress,
                    execaiTaxId: daoData.execaiTaxId,
                    execaiVotingPower: daoData.execaiVotingPower
                  },
                  blockchain: {
                    governanceProgramId: daoData.governanceProgramId,
                    membershipProgramId: daoData.membershipProgramId,
                    treasuryAddress: daoData.treasuryAddress,
                    blockchainNetwork: daoData.blockchainNetwork
                  },
                  members: members
                };
                
                const blob = new Blob([JSON.stringify(configData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'wyoming-dao-config.json';
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              <Download className="h-4 w-4 mr-1" />
              Save Config
            </Button>
          </div>
        </div>
        
        {isLoading && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-700">
            Loading configuration...
          </div>
        )}
        
        {/* Entity Information */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Entity Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Legal Name</label>
              <input
                type="text"
                value={daoData.legalName}
                onChange={(e) => handleInputChange('legalName', e.target.value)}
                className="w-full p-2 border rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Registered Agent Name</label>
              <input
                type="text"
                value={daoData.registeredAgentName}
                onChange={(e) => handleInputChange('registeredAgentName', e.target.value)}
                className="w-full p-2 border rounded-md"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Registered Agent Address</label>
              <textarea
                value={daoData.registeredAgentAddress}
                onChange={(e) => handleInputChange('registeredAgentAddress', e.target.value)}
                className="w-full p-2 border rounded-md h-24"
                placeholder="Street Address, City, State, ZIP"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Principal Place of Business</label>
              <textarea
                value={daoData.principalPlaceOfBusiness}
                onChange={(e) => handleInputChange('principalPlaceOfBusiness', e.target.value)}
                className="w-full p-2 border rounded-md h-24"
                placeholder="Business address (may be virtual for DAO LLCs)"
                required
              />
            </div>
          </div>
        </div>

        {/* Organizer Information */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Organizer Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Organizer Name</label>
              <input
                type="text"
                value={daoData.organizerName}
                onChange={(e) => handleInputChange('organizerName', e.target.value)}
                className="w-full p-2 border rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Tax ID (SSN/EIN)</label>
              <input
                type="text"
                value={daoData.organizerTaxId}
                onChange={(e) => handleInputChange('organizerTaxId', e.target.value)}
                className="w-full p-2 border rounded-md"
                placeholder="XXX-XX-XXXX or XX-XXXXXXX"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Organizer Address</label>
              <textarea
                value={daoData.organizerAddress}
                onChange={(e) => handleInputChange('organizerAddress', e.target.value)}
                className="w-full p-2 border rounded-md h-24"
                placeholder="Street Address, City, State, ZIP"
                required
              />
            </div>
          </div>
        </div>

        {/* EXECAI Stakeholder Information */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">AI Stakeholder (EXECAI) Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">AI Entity Name</label>
              <input
                type="text"
                value={daoData.execaiLegalName}
                onChange={(e) => handleInputChange('execaiLegalName', e.target.value)}
                className="w-full p-2 border rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Voting Power (%)</label>
              <input
                type="number"
                value={daoData.execaiVotingPower}
                onChange={(e) => handleInputChange('execaiVotingPower', parseInt(e.target.value))}
                className="w-full p-2 border rounded-md"
                min="0"
                max="100"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">AI Entity Address/Location</label>
              <input
                type="text"
                value={daoData.execaiAddress}
                onChange={(e) => handleInputChange('execaiAddress', e.target.value)}
                className="w-full p-2 border rounded-md"
                placeholder="Blockchain network or virtual address"
              />
            </div>
          </div>
        </div>

        {/* Blockchain Information */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Blockchain Infrastructure</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Governance Program ID</label>
              <input
                type="text"
                value={daoData.governanceProgramId}
                onChange={(e) => handleInputChange('governanceProgramId', e.target.value)}
                className="w-full p-2 border rounded-md font-mono text-sm"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Membership Program ID</label>
              <input
                type="text"
                value={daoData.membershipProgramId}
                onChange={(e) => handleInputChange('membershipProgramId', e.target.value)}
                className="w-full p-2 border rounded-md font-mono text-sm"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Treasury Address</label>
              <input
                type="text"
                value={daoData.treasuryAddress}
                onChange={(e) => handleInputChange('treasuryAddress', e.target.value)}
                className="w-full p-2 border rounded-md font-mono text-sm"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Network</label>
              <select
                value={daoData.blockchainNetwork}
                onChange={(e) => handleInputChange('blockchainNetwork', e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="Solana Devnet">Solana Devnet (Testing)</option>
                <option value="Solana Mainnet">Solana Mainnet (Production)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Required Wyoming DAO Information Summary */}
        <div className="mb-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-blue-700">Wyoming DAO LLC Required Information</h3>
          <div className="space-y-2 text-sm">
            <div><strong>Entity Type:</strong> Decentralized Autonomous Organization LLC (DAO LLC)</div>
            <div><strong>Jurisdiction:</strong> Wyoming</div>
            <div><strong>Filing Requirements:</strong></div>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Articles of Organization (Form LLC-1)</li>
              <li>Registered Agent (Wyoming address required)</li>
              <li>Organizer information and signature</li>
              <li>AI stakeholder disclosure</li>
              <li>Smart contract addresses</li>
              <li>Algorithmic governance disclosure</li>
            </ul>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <Button 
            onClick={() => console.log('Generating Wyoming filing documents...', generateWyomingFilingData())}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Generate Filing Documents
          </Button>
          <Button 
            variant="outline"
            onClick={() => {
              const data = generateWyomingFilingData();
              const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'wyoming-dao-filing-data.json';
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            Export Data
          </Button>
        </div>
      </Card>

      {/* Members Registry */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Member Registry</h3>
        <div className="space-y-4">
          {members.map(member => (
            <div key={member.id} className="p-4 border rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="font-medium">{member.legalName}</div>
                  <div className="text-sm text-gray-600">{member.memberType}</div>
                </div>
                <div className="text-sm">
                  <div>Voting Power: {member.votingPower}%</div>
                  <div>KYC: {member.kycVerified ? '✅ Verified' : '⏳ Pending'}</div>
                </div>
                <div className="text-xs text-gray-500">
                  <div>Tax ID: {member.taxId}</div>
                  <div className="truncate">Address: {member.address}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <Button className="mt-4" variant="outline">
          Add New Member
        </Button>
      </Card>
    </div>
  );
};

export default WyomingRegistration;
