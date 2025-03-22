 ## Requirements Analysis

### Problem Background

With the development of globalization and digitization, cross-border e-commerce has rapidly emerged as a new business model. Cross-border e-commerce refers to the sale of goods or services via the internet across national or regional borders, enabling international trade. Its main forms include B2B (business-to-business), B2C (business-to-consumer), and C2C (consumer-to-consumer), covering a wide range of product categories such as clothing, electronics, household goods, cosmetics, and food. In cross-border e-commerce transactions, consumers can select desired products from a global pool, while sellers can expand into overseas markets, achieving global sales.

At the same time, cross-border payments, a critical component of cross-border e-commerce transactions, are also evolving. Traditional cross-border payment methods suffer from low efficiency, high costs, and insufficient transaction transparency. Blockchain technology, with its unique features of immutability and decentralization, demonstrates significant potential in the field of cross-border payments. In recent years, blockchain-based cross-border payments, as a product of financial innovation driven by emerging technology, have garnered widespread attention. Their application has effectively addressed some issues in traditional cross-border payments, but challenges remain, including the unification of technical standards, adaptation to regulatory policies, and scaling user adoption.

Under the RCEP (Regional Comprehensive Economic Partnership) framework, cross-border e-commerce in East Asia and Southeast Asia is experiencing robust growth, with an average annual growth rate of 23%. However, logistics in this region face numerous challenges. Logistics costs account for 28%-35% of the goods' value, far exceeding the global average of 15%. The core contradictions in traditional cross-border logistics are primarily reflected in the following aspects:

1. **Fragmented Processes**: Cargo transportation involves 6–8 intermediaries, such as freight forwarders, customs brokers, and land transport agents. Information silos between these stages lead to isolated data, resulting in transportation cycles of 18–25 days, significantly reducing logistics efficiency.
2. **High Compliance Costs**: Cross-border KYC (Know Your Customer) and AML (Anti-Money Laundering) reviews rely on manual processing, averaging 4.7 hours per shipment with an error rate of 12%. This not only increases labor costs but also leads to audit errors, affecting the normal transport of goods.
3. **Uncontrolled Environmental Costs**: Container empty load rates reach 34%, and carbon emission intensity per unit of cargo is 41% higher than EU standards, with a lack of quantitative regulatory measures. This not only wastes resources but also places significant pressure on the environment.

The causes of these issues include significant differences in laws, regulations, currency exchange rates, languages, and cultures across countries and regions, increasing the coordination difficulty of cross-border logistics and payments; the numerous stages in cross-border logistics lack effective information sharing and collaboration mechanisms; the absence of unified logistics standards and norms makes it difficult to ensure the efficiency and quality of logistics operations; and insufficient attention to and regulation of environmental costs reduces the motivation for logistics companies to lower carbon emissions.

Previously, the TradeLens project, launched by Maersk and IBM, attempted to leverage blockchain technology to address issues in cross-border logistics. TradeLens aimed to create a global shipping logistics information-sharing platform, using blockchain to enable transparent and shared logistics data, thereby improving efficiency and security. However, the project ultimately failed, primarily due to:

1. **Difficulty in Industry Integration**: Cross-border logistics involves numerous stakeholders, including shipping companies, freight forwarders, ports, and customs, each with differing interests and demands. Reaching a unified cooperation agreement proved challenging, limiting the platform’s promotion and adoption.
2. **Data Privacy and Security Concerns**: Although blockchain offers a degree of security, companies remained wary of data privacy and security in practice, reluctant to upload critical data to the platform.
3. **Lack of Unified Technical Standards**: Variations in technical standards across enterprises and regions resulted in poor data compatibility and interoperability, impacting the platform’s overall performance.

From the failure of TradeLens, we can draw lessons that a blockchain-based cross-border e-commerce logistics system should meet the following conditions:

1. **Multi-Party Collaboration**: It should coordinate all participants in cross-border logistics, establishing a unified cooperation mechanism to enable data sharing and collaborative operations.
2. **Data Security and Privacy Protection**: While ensuring data sharing, it must fully protect the data privacy and security of businesses and users, employing advanced encryption and privacy protection mechanisms.
3. **Unified Technical Standards**: It should establish uniform technical standards and norms to ensure data compatibility and interoperability across different systems and platforms.
4. **Compliance**: It must comply with the laws, regulations, and supervisory requirements of different countries and regions, effectively addressing compliance issues in cross-border logistics.

---

### Solution

To address these pain points, we propose a series of innovative approaches. Our solution incorporates six key innovations: distributed ledger, decentralized bidding, token economy, smart payments, API integration, and identity verification with CLP (Container Load Plan).

The introduction of a distributed ledger aims to resolve process fragmentation and information opacity. In traditional logistics, information is isolated at each stage, forming silos. A distributed ledger—whether simulated in a pseudo-distributed manner or supported by true distribution—enables information sharing and transparency, allowing all participants (cross-border e-commerce merchants, warehousing companies, shipping companies, local transport firms, and buyers) to access real-time logistics data, breaking down information barriers and improving efficiency.

Decentralized bidding seeks to reduce logistics costs and optimize solutions. Traditional logistics involves multiple intermediaries, increasing costs and lacking effective bidding mechanisms. Multi-stage bidding and multimodal transport optimization allow participants to compete directly, offering more reasonable quotes while generating optimal solutions based on different needs (cost-effective, balanced, or green), thereby reducing costs and enhancing transport efficiency.

The token economy is designed to incentivize green transportation and maintain system stability. The uncontrolled environmental costs in cross-border logistics lack quantitative oversight. Through super node rewards, carbon emission compensation incentives, and a credit scoring mechanism, participants are encouraged to adopt green transport routes, reducing emissions while motivating nodes to actively maintain the ledger, ensuring the system’s smooth operation.

Smart payments aim to address payment efficiency and security issues. Traditional cross-border payments are inefficient, costly, and lack transparency. A layered architecture with milestone-triggered payments tied to logistics events, combined with compliance checks, enhances payment efficiency, ensures security and fairness, and reduces risks.

API integration is intended to acquire critical external data and achieve system interoperability. Cross-border logistics involves data needs such as carbon footprint calculation, logistics tracking, KYC/AML verification, distance computation, and exchange rate conversion. By integrating these APIs, the system can interact with external platforms, obtaining necessary data to optimize logistics solutions and facilitate payment processing.

Identity verification with CLP ensures transaction authenticity and compliance. Fraudulent transactions and compliance challenges are common in cross-border logistics. Using CLP to verify the authenticity of demand, bids, and payments—along with support for simulated signatures and future digital signatures/DID—effectively prevents fraud, ensures transactions are based on real cargo data, and meets compliance requirements across different regions.

#### Distributed Ledger
Considering the need for rapid concept validation and demonstration, we designed a pseudo-distributed mode with multi-node collaboration on a single machine to avoid the complexity and high costs of building a real network. This approach simulates multiple nodes on one device, using a pseudo-consensus mechanism to mimic the consensus process in a real network. This design quickly showcases the features of a distributed ledger, allowing users to experience the system’s core functions in the early stages without requiring a complex network setup.

To demonstrate the system’s potential and scalability in a real blockchain environment, we reserved an interface for the Ethereum Sepolia testnet. This allows for easy migration to a true distributed network in the future, leveraging the infrastructure and security of the Ethereum testnet to prepare for large-scale application and deployment.

#### Decentralized Bidding
A blind auction combined with optimized multi-stage bidding ensures fairness and efficiency in the bidding process. The blind auction phase prevents collusion among participants, making bids more reflective of true costs and market conditions. The subsequent optimization phase adjusts solutions based on factors like carbon emissions and timeliness, yielding superior logistics plans.

We designed three multimodal transport options—cost-effective, balanced, and green—to meet diverse user needs. Users prioritize different aspects of logistics, such as cost, overall benefits, or environmental impact. By offering multiple options, the system adapts to varied market demands, enhancing user satisfaction.

#### Token Economy
To encourage nodes to actively maintain the ledger, we designed a mechanism where super nodes are rewarded for their efforts. Super nodes play critical roles in the system, such as data storage and transaction verification. Rewards increase their engagement and stability, ensuring the system’s reliable operation.

To address the uncontrolled environmental costs in cross-border logistics, we introduced a carbon emission compensation incentive. By rewarding participants with tokens for adopting green transport routes, we encourage logistics firms to reduce emissions, promoting sustainability.

A credit scoring mechanism based on transaction history creates credit profiles for participants. High-scoring participants gain greater trust, accessing more collaboration opportunities and preferential policies, fostering a healthy logistics ecosystem.

#### Smart Payments
We designed a layered architecture with large transactions on the main chain and small transactions on a sidechain to enhance payment efficiency and flexibility. The main chain handles large payments for security and reliability, while the sidechain processes small payments for speed and throughput. This structure meets the needs of transactions of varying scales, optimizing the payment experience.

Payments are tied to logistics milestones (e.g., warehousing, customs clearance, delivery) and include compliance checks to ensure security and fairness. Payments are triggered only when milestones are reached and compliance is verified, reducing risks and protecting the interests of both parties.

#### API Integration
To enable the system to acquire critical external data and interact with external platforms, we integrated APIs for carbon footprint calculation, logistics tracking, KYC/AML verification, distance computation, and exchange rate conversion. For instance, the carbon footprint API supports the carbon emission compensation mechanism; the logistics tracking API provides real-time cargo status updates; the KYC/AML verification API addresses compliance issues; and the distance and exchange rate APIs provide essential data for logistics optimization and payments.

#### Identity Verification with CLP
To optimize identity verification, we use CLP to validate the authenticity of demand, bids, and payments, effectively preventing fraudulent transactions. CLP contains detailed cargo information, and verifying its authenticity ensures transactions are based on real data, enhancing system reliability and security.

To meet needs at different stages, the system supports simulated signatures and future digital signatures/DID. Simulated signatures enable rapid identity verification during development and testing, while digital signatures and DID offer enhanced security and privacy protection for real-world applications in the future.

