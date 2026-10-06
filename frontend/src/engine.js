export const weights={soil_degradation_risk:.25,vegetation_stress:.2,water_stress:.15,habitat_degradation:.15,biodiversity_risk:.15,human_pressure_index:.1};
export const labels={soil_degradation_risk:'Soil degradation',vegetation_stress:'Vegetation stress',water_stress:'Water stress',habitat_degradation:'Habitat degradation',biodiversity_risk:'Biodiversity risk',human_pressure_index:'Human pressure'};
const clip=x=>Math.max(0,Math.min(100,x));
export function classify(score){if(!Number.isFinite(score)||score<0||score>100)throw Error('Score must be between 0 and 100');return score<=25?'LOW':score<=50?'MODERATE':score<=75?'HIGH':'CRITICAL'}
export function scoreZone(z){
 const fields=['vegetation_index','forest_cover','soil_degradation','slope','water_availability','rainfall','drought_index','habitat_quality','biodiversity_index','human_pressure','land_use_change'];
 const missing=fields.filter(k=>!Number.isFinite(z[k]));
 const v=k=>Number.isFinite(z[k])?clip(z[k]):50;
 const i={vegetation_stress:.6*(100-v('vegetation_index'))+.4*(100-v('forest_cover')),soil_degradation_risk:.75*v('soil_degradation')+.25*clip((Number.isFinite(z.slope)?z.slope:15)/60*100),water_stress:.4*(100-v('water_availability'))+.25*(100-v('rainfall'))+.35*v('drought_index'),habitat_degradation:100-v('habitat_quality'),biodiversity_risk:100-v('biodiversity_index'),human_pressure_index:.65*v('human_pressure')+.35*v('land_use_change')};
 Object.keys(i).forEach(k=>i[k]=Math.round(i[k]*100)/100);
 const score=Math.round(Object.entries(weights).reduce((s,[k,w])=>s+i[k]*w,0)*100)/100;
 const drivers=Object.entries(weights).map(([k,w])=>({key:k,name:labels[k],value:i[k],weight:w,contribution:i[k]*w})).sort((a,b)=>b.contribution-a.contribution);
 const intervention={soil_degradation_risk:'Soil conservation',vegetation_stress:'Native vegetation restoration',water_stress:'Rainwater harvesting',habitat_degradation:'Habitat restoration',biodiversity_risk:'Biodiversity restoration',human_pressure_index:'Community land stewardship'}[drivers[0].key];
 return {...z,indicators:i,score,priority:classify(score),drivers,intervention,missing,completeness:Math.round((fields.length-missing.length)/fields.length*100)};
}
export function simulate(z,recovery){if(!Number.isFinite(recovery)||recovery<0||recovery>50)throw Error('Recovery must be 0–50');const p=recovery/100;const next={...z};for(const k of ['vegetation_index','forest_cover','water_availability','habitat_quality','biodiversity_index']){if(Number.isFinite(z[k]))next[k]=z[k]+(100-z[k])*p}for(const k of ['soil_degradation','drought_index','human_pressure','land_use_change']){if(Number.isFinite(z[k]))next[k]=z[k]*(1-p)}return scoreZone(next)}
export function shortlist(zones,budget,cost){if(!Number.isFinite(budget)||budget<0||!Number.isFinite(cost)||cost<=0)throw Error('Enter a valid budget and positive cost');return [...zones].filter(z=>z.missing.length===0).sort((a,b)=>b.score-a.score||a.zone_id.localeCompare(b.zone_id)).slice(0,Math.floor(budget/cost))}
