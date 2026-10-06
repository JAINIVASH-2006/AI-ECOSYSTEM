// Comprehensive Ecological Zones & Decision-Support Data for EcoRestore AI
export const REGIONS = [
  "All Regions",
  "Cauvery Basin & Tamil Nadu",
  "Western Ghats Biodiversity Hotspot",
  "Nilgiris Biosphere Reserve",
  "Deccan Plateau Drylands",
  "Eastern Ghats Escarpment",
  "Sundarbans Mangrove Delta",
  "Aravalli Semi-Arid Ridge",
  "Central Indian Forest Corridor"
];

export const PRIORITY_TIERS = {
  CRITICAL: { label: "Critical", color: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe", min: 81, max: 100 },
  HIGH: { label: "High", color: "#ef4444", bg: "#fef2f2", border: "#fecaca", min: 61, max: 80 },
  MODERATE: { label: "Moderate", color: "#f59e0b", bg: "#fffbeb", border: "#fde68a", min: 41, max: 60 },
  LOW: { label: "Low", color: "#10b981", bg: "#ecfdf5", border: "#a7f3d0", min: 21, max: 40 },
  VERY_LOW: { label: "Very Low", color: "#059669", bg: "#f0fdf4", border: "#bbf7d0", min: 0, max: 20 },
};

export const ZONES_DATA = [
  {
    id: "zone-tn-01",
    name: "Cauvery Riverbed Delta Riparian Zone",
    region: "Cauvery Basin & Tamil Nadu",
    lat: 10.9601,
    lng: 78.0766,
    priorityScore: 88,
    priorityTier: "CRITICAL",
    healthScore: 32,
    areaHa: 4200,
    ndvi: 0.24,
    soilOrganicCarbon: 0.42, // %
    soilMoisture: 18, // %
    annualRainfall: 740, // mm
    biodiversityIndex: 38, // 0-100
    humanPressureIndex: 78, // 0-100
    erosionHazard: "Severe",
    primaryThreat: "Severe Sand Mining & Riparian Desiccation",
    secondaryThreat: "Runoff Contamination & Weed Colonization",
    threats: ["Deforestation", "Soil Erosion", "Water Scarcity", "High Human Pressure"],
    recommendedIntervention: "Riparian Buffer Reconstruction & Vetiver Bio-fencing",
    interventionDetails: "Establish a 50m multi-tiered indigenous riparian buffer with deep-rooting grasses and moisture-retaining trees to halt bank scouring.",
    recommendedSpecies: [
      { name: "Vetiver Grass (Chrysopogon zizanioides)", type: "Soil-Binding Grass", survivalRate: "94%", waterNeed: "Low" },
      { name: "Neem (Azadirachta indica)", type: "Canopy Tree", survivalRate: "89%", waterNeed: "Low" },
      { name: "Arjun Tree (Terminalia arjuna)", type: "Riparian Tree", survivalRate: "86%", waterNeed: "Medium" },
      { name: "Pongamia (Millettia pinnata)", type: "Nitrogen Fixer", survivalRate: "91%", waterNeed: "Low-Med" }
    ],
    carbonOffsetEstimate: 24500, // tCO2e / 5yr
    estCostLakhs: 48.5,
    weather: { temp: 31.4, humidity: 62, condition: "Partly Cloudy", windSpeed: 14 }
  },
  {
    id: "zone-wg-02",
    name: "Agasthyamalai Rainforest Fringe Corridor",
    region: "Western Ghats Biodiversity Hotspot",
    lat: 8.6186,
    lng: 77.2477,
    priorityScore: 76,
    priorityTier: "HIGH",
    healthScore: 45,
    areaHa: 6800,
    ndvi: 0.51,
    soilOrganicCarbon: 1.15,
    soilMoisture: 42,
    annualRainfall: 1980,
    biodiversityIndex: 82,
    humanPressureIndex: 64,
    erosionHazard: "High Slope Runoff",
    primaryThreat: "Habitat Fragmentation & Monoculture Encroachment",
    secondaryThreat: "Invasive Lantana camara Expansion",
    threats: ["Habitat Loss", "Biodiversity Decline", "Invasive Species"],
    recommendedIntervention: "Native Wildlife Corridor Enrichment & Invasive Eradication",
    interventionDetails: "Systematic manual eradication of Lantana camara accompanied by high-density enrichment planting of endemic evergreen fruiting species.",
    recommendedSpecies: [
      { name: "Wild Jack (Artocarpus hirsutus)", type: "Evergreen Canopy", survivalRate: "92%", waterNeed: "Medium" },
      { name: "Ironwood (Mesua ferrea)", type: "Keystone Species", survivalRate: "87%", waterNeed: "High" },
      { name: "Indian Rosewood (Dalbergia latifolia)", type: "Hardwood", survivalRate: "85%", waterNeed: "Medium" },
      { name: "Malabar Tamarind (Garcinia gummi-gutta)", type: "Understory Tree", survivalRate: "88%", waterNeed: "Medium" }
    ],
    carbonOffsetEstimate: 51200,
    estCostLakhs: 72.0,
    weather: { temp: 26.2, humidity: 84, condition: "Humid / Light Mist", windSpeed: 9 }
  },
  {
    id: "zone-nl-03",
    name: "Nilgiris Shola-Grassland Mosaic Restoration",
    region: "Nilgiris Biosphere Reserve",
    lat: 11.4102,
    lng: 76.6950,
    priorityScore: 84,
    priorityTier: "CRITICAL",
    healthScore: 39,
    areaHa: 3100,
    ndvi: 0.38,
    soilOrganicCarbon: 1.45,
    soilMoisture: 35,
    annualRainfall: 1650,
    biodiversityIndex: 79,
    humanPressureIndex: 71,
    erosionHazard: "Moderate Slumping",
    primaryThreat: "Historical Eucalyptus & Wattle Infestation",
    secondaryThreat: "Wetland Micro-drainage Disruption",
    threats: ["Habitat Loss", "Water Scarcity", "Vegetation Loss"],
    recommendedIntervention: "Shola Regeneration & Native Grassland Reseeding",
    interventionDetails: "Phased removal of exotic wattle coppices coupled with Shola nursery sapling transplanting and watershed headwater swale construction.",
    recommendedSpecies: [
      { name: "Syzygium densiflorum (Kattunaval)", type: "Shola Native", survivalRate: "90%", waterNeed: "Medium" },
      { name: "Litsea wightiana", type: "Montane Sub-canopy", survivalRate: "86%", waterNeed: "Medium" },
      { name: "Cymbopogon flexuosus (Lemon Grass)", type: "Highland Grass", survivalRate: "95%", waterNeed: "Low" },
      { name: "Rhododendron arboreum", type: "High-Altitude Tree", survivalRate: "82%", waterNeed: "Med-High" }
    ],
    carbonOffsetEstimate: 29800,
    estCostLakhs: 55.4,
    weather: { temp: 19.5, humidity: 76, condition: "Overcast", windSpeed: 16 }
  },
  {
    id: "zone-dp-04",
    name: "Rayalaseema Semi-Arid Watershed Basin",
    region: "Deccan Plateau Drylands",
    lat: 14.6819,
    lng: 77.6006,
    priorityScore: 92,
    priorityTier: "CRITICAL",
    healthScore: 22,
    areaHa: 9500,
    ndvi: 0.16,
    soilOrganicCarbon: 0.28,
    soilMoisture: 9,
    annualRainfall: 520,
    biodiversityIndex: 26,
    humanPressureIndex: 68,
    erosionHazard: "Severe Wind & Sheet Erosion",
    primaryThreat: "Acute Groundwater Table Collapse & Desertification",
    secondaryThreat: "Soil Salinization & Biomass Depletion",
    threats: ["Desertification Risk", "Water Scarcity", "Soil Degradation", "Land Degradation"],
    recommendedIntervention: "Catchment Contour Bunding & Dryland Agroforestry",
    interventionDetails: "Construct 45 check-dams and percolation ponds; intercrop hardy drought-resilient legumes with deep-taproot timber species.",
    recommendedSpecies: [
      { name: "Prosopis cineraria (Khejri)", type: "Nitrogen Dryland Tree", survivalRate: "96%", waterNeed: "Very Low" },
      { name: "Indian Gooseberry (Aonla)", type: "Horticultural Timber", survivalRate: "91%", waterNeed: "Low" },
      { name: "Ber / Jujube (Ziziphus mauritiana)", type: "Fruit Shrub", survivalRate: "93%", waterNeed: "Very Low" },
      { name: "Subabul (Leucaena leucocephala)", type: "Fodder & Fencing", survivalRate: "90%", waterNeed: "Low" }
    ],
    carbonOffsetEstimate: 38700,
    estCostLakhs: 64.2,
    weather: { temp: 35.8, humidity: 38, condition: "Sunny / Dry", windSpeed: 18 }
  },
  {
    id: "zone-eg-05",
    name: "Eastern Ghats Shevaroy Range Slopes",
    region: "Eastern Ghats Escarpment",
    lat: 11.8333,
    lng: 78.2167,
    priorityScore: 68,
    priorityTier: "HIGH",
    healthScore: 52,
    areaHa: 5300,
    ndvi: 0.44,
    soilOrganicCarbon: 0.82,
    soilMoisture: 28,
    annualRainfall: 1100,
    biodiversityIndex: 64,
    humanPressureIndex: 58,
    erosionHazard: "Moderate Gully Erosion",
    primaryThreat: "Unregulated Bauxite Mining Margins & Soil Loss",
    secondaryThreat: "Seasonal Forest Fires",
    threats: ["Soil Erosion", "Deforestation", "Soil Degradation"],
    recommendedIntervention: "Slope Stabilization with Terracing & Mixed Deciduous Plantation",
    interventionDetails: "Terraced bio-engineering retaining walls planted with native fast-growing bamboo and deciduous hardwoods to trap runoff sediments.",
    recommendedSpecies: [
      { name: "Indian Sandalwood (Santalum album)", type: "Semi-parasitic Hardwood", survivalRate: "83%", waterNeed: "Low-Med" },
      { name: "Solid Bamboo (Dendrocalamus strictus)", type: "Soil Stabilizer", survivalRate: "95%", waterNeed: "Low" },
      { name: "Sal Tree (Shorea robusta)", type: "Canopy Hardwood", survivalRate: "87%", waterNeed: "Medium" },
      { name: "Mahua (Madhuca longifolia)", type: "Multi-purpose Tree", survivalRate: "92%", waterNeed: "Low" }
    ],
    carbonOffsetEstimate: 41000,
    estCostLakhs: 42.0,
    weather: { temp: 28.1, humidity: 65, condition: "Clear Sky", windSpeed: 11 }
  },
  {
    id: "zone-sb-06",
    name: "Sundarbans Mudflat Coastal Surge Buffer",
    region: "Sundarbans Mangrove Delta",
    lat: 21.9497,
    lng: 88.8997,
    priorityScore: 79,
    priorityTier: "HIGH",
    healthScore: 48,
    areaHa: 7800,
    ndvi: 0.58,
    soilOrganicCarbon: 1.82,
    soilMoisture: 72,
    annualRainfall: 1850,
    biodiversityIndex: 91,
    humanPressureIndex: 62,
    erosionHazard: "Tidal Embankment Breaching",
    primaryThreat: "Cyclonic Surge Erosion & Hyper-salinization",
    secondaryThreat: "Aquaculture Effluent Runoff",
    threats: ["Habitat Loss", "Soil Erosion", "High Human Pressure"],
    recommendedIntervention: "Mangrove Tidal Mudflat Afforestation",
    interventionDetails: "Inter-tidal mudflat prop-root species planting (Rhizophora & Avicennia) combined with bamboo geotextile silt traps.",
    recommendedSpecies: [
      { name: "Sundari (Heritiera fomes)", type: "Core Mangrove", survivalRate: "85%", waterNeed: "Tidal Saline" },
      { name: "Grey Mangrove (Avicennia marina)", type: "Frontline Silt Trap", survivalRate: "94%", waterNeed: "High Saline" },
      { name: "Spotted Mangrove (Rhizophora mucronata)", type: "Stilt Root Protector", survivalRate: "91%", waterNeed: "Tidal Saline" },
      { name: "Golpata / Nypa Palm", type: "Bank Stabilizer", survivalRate: "89%", waterNeed: "Brackish" }
    ],
    carbonOffsetEstimate: 78000,
    estCostLakhs: 88.0,
    weather: { temp: 29.3, humidity: 88, condition: "Coastal Breeze", windSpeed: 22 }
  },
  {
    id: "zone-av-07",
    name: "Aravalli Mining Reclaim & Eco-Shield",
    region: "Aravalli Semi-Arid Ridge",
    lat: 28.2560,
    lng: 76.9200,
    priorityScore: 86,
    priorityTier: "CRITICAL",
    healthScore: 28,
    areaHa: 4900,
    ndvi: 0.19,
    soilOrganicCarbon: 0.31,
    soilMoisture: 11,
    annualRainfall: 580,
    biodiversityIndex: 34,
    humanPressureIndex: 85,
    erosionHazard: "Severe Rock Quarry Dust & Slag",
    primaryThreat: "Quarrying Scars & Desert Dust Encroachment",
    secondaryThreat: "Illegal Real-Estate Fragmentation",
    threats: ["Land Degradation", "Desertification Risk", "High Human Pressure", "Soil Degradation"],
    recommendedIntervention: "Eco-Restoration Mining Pit Reclamation & Green Wall",
    interventionDetails: "Topsoil replenishment with microbial biochar compost, pit backfilling, and multi-layer green wall shield against dust storms.",
    recommendedSpecies: [
      { name: "Dhau (Anogeissus pendula)", type: "Ridge Native", survivalRate: "94%", waterNeed: "Very Low" },
      { name: "Kumtha (Acacia senegal)", type: "Gum Arabic Native", survivalRate: "93%", waterNeed: "Low" },
      { name: "Guggul (Commiphora wightii)", type: "Medicinal Shrub", survivalRate: "88%", waterNeed: "Very Low" },
      { name: "Babool (Acacia nilotica)", type: "Deep-Root Binder", survivalRate: "95%", waterNeed: "Low" }
    ],
    carbonOffsetEstimate: 31500,
    estCostLakhs: 59.5,
    weather: { temp: 33.2, humidity: 44, condition: "Hazy Sun", windSpeed: 15 }
  },
  {
    id: "zone-ci-08",
    name: "Kanha-Pench Wildlife Forest Corridor",
    region: "Central Indian Forest Corridor",
    lat: 21.9312,
    lng: 79.8456,
    priorityScore: 54,
    priorityTier: "MODERATE",
    healthScore: 65,
    areaHa: 8900,
    ndvi: 0.63,
    soilOrganicCarbon: 1.05,
    soilMoisture: 38,
    annualRainfall: 1350,
    biodiversityIndex: 88,
    humanPressureIndex: 42,
    erosionHazard: "Low to Moderate",
    primaryThreat: "Highway Linear Infrastructure Severance",
    secondaryThreat: "Grazing Pressure at Peripheral Villages",
    threats: ["Habitat Loss", "Biodiversity Decline"],
    recommendedIntervention: "Canopy Overpass Enrichment & Community Stall-Feeding Buffer",
    interventionDetails: "Underpass and eco-duct vegetative masking using native browse species and village community woodlot plantations.",
    recommendedSpecies: [
      { name: "Mahua (Madhuca longifolia)", type: "Community Keystone", survivalRate: "93%", waterNeed: "Medium" },
      { name: "Tendu (Diospyros melanoxylon)", type: "Non-Timber Forest Species", survivalRate: "90%", waterNeed: "Low-Med" },
      { name: "Bamboo (Bambusa bambos)", type: "Understory Shelter", survivalRate: "96%", waterNeed: "Medium" },
      { name: "Palas / Flame of Forest (Butea monosperma)", type: "Pollinator Magnet", survivalRate: "94%", waterNeed: "Low" }
    ],
    carbonOffsetEstimate: 62000,
    estCostLakhs: 36.8,
    weather: { temp: 27.5, humidity: 58, condition: "Partly Cloudy", windSpeed: 10 }
  },
  {
    id: "zone-tn-09",
    name: "Pichavaram Mangrove Wetland Sanctuary",
    region: "Cauvery Basin & Tamil Nadu",
    lat: 11.4285,
    lng: 79.7820,
    priorityScore: 62,
    priorityTier: "HIGH",
    healthScore: 58,
    areaHa: 2800,
    ndvi: 0.61,
    soilOrganicCarbon: 1.60,
    soilMoisture: 68,
    annualRainfall: 1250,
    biodiversityIndex: 86,
    humanPressureIndex: 51,
    erosionHazard: "Estuarine Current Scouring",
    primaryThreat: "Reduced Freshwater Inflow & Canal Siltation",
    secondaryThreat: "Plastic & Urban Debris Inundation",
    threats: ["Water Scarcity", "Habitat Loss", "High Human Pressure"],
    recommendedIntervention: "Fishbone Canal De-siltation & Prop-Root Nursery Propagation",
    interventionDetails: "Hydrological restoration via manual de-silting of feeder channels to revive tidal flushing, coupled with community seedling rearing.",
    recommendedSpecies: [
      { name: "Avicennia marina (Grey Mangrove)", type: "Salt-Excreting Pioneer", survivalRate: "96%", waterNeed: "Tidal" },
      { name: "Rhizophora apiculata", type: "Stilt Root Shrub", survivalRate: "92%", waterNeed: "Tidal" },
      { name: "Excoecaria agallocha (Blinding Tree)", type: "High-Tide Border", survivalRate: "88%", waterNeed: "Brackish" },
      { name: "Aegiceras corniculatum", type: "Flowering River Bush", survivalRate: "86%", waterNeed: "Brackish" }
    ],
    carbonOffsetEstimate: 34000,
    estCostLakhs: 29.0,
    weather: { temp: 30.1, humidity: 79, condition: "Sea Breeze", windSpeed: 17 }
  },
  {
    id: "zone-tn-10",
    name: "Anaimalai Foothills Grassland & Riparian Strip",
    region: "Western Ghats Biodiversity Hotspot",
    lat: 10.4500,
    lng: 76.9800,
    priorityScore: 42,
    priorityTier: "MODERATE",
    healthScore: 71,
    areaHa: 3600,
    ndvi: 0.69,
    soilOrganicCarbon: 1.25,
    soilMoisture: 46,
    annualRainfall: 1720,
    biodiversityIndex: 89,
    humanPressureIndex: 38,
    erosionHazard: "Low",
    primaryThreat: "Invasive Weed Encroachment in Peripheral Clearings",
    secondaryThreat: "Seasonal Dry-Spell Wildfires",
    threats: ["Invasive Species", "Vegetation Loss"],
    recommendedIntervention: "Assisted Natural Regeneration (ANR) & Fire-breaks",
    interventionDetails: "Establish green fire-break corridors of succulent native species and protect natural regeneration saplings with bio-fencing.",
    recommendedSpecies: [
      { name: "Indian Laurel (Terminalia elliptica)", type: "Fire-Resistant Tree", survivalRate: "95%", waterNeed: "Medium" },
      { name: "Kadam (Neolamarckia cadamba)", type: "Fast Growing Canopy", survivalRate: "91%", waterNeed: "High" },
      { name: "Indian Gooseberry", type: "Understory Pioneer", survivalRate: "93%", waterNeed: "Low-Med" }
    ],
    carbonOffsetEstimate: 28500,
    estCostLakhs: 21.5,
    weather: { temp: 24.8, humidity: 72, condition: "Fresh Breeze", windSpeed: 12 }
  }
];

// Helper calculations
export function getOverallStats(zones = ZONES_DATA) {
  const totalZones = zones.length;
  if (totalZones === 0) return { avgHealth: 0, totalHa: 0, criticalCount: 0, avgNdvi: 0, totalCarbon: 0, avgCost: 0 };

  const totalHa = zones.reduce((acc, z) => acc + z.areaHa, 0);
  const avgHealth = Math.round(zones.reduce((acc, z) => acc + z.healthScore, 0) / totalZones);
  const criticalCount = zones.filter(z => z.priorityTier === "CRITICAL" || z.priorityTier === "HIGH").length;
  const avgNdvi = (zones.reduce((acc, z) => acc + z.ndvi, 0) / totalZones).toFixed(2);
  const totalCarbon = zones.reduce((acc, z) => acc + z.carbonOffsetEstimate, 0);
  const totalCost = zones.reduce((acc, z) => acc + z.estCostLakhs, 0).toFixed(1);

  return {
    totalZones,
    totalHa,
    avgHealth,
    criticalCount,
    avgNdvi,
    totalCarbon,
    totalCost
  };
}
