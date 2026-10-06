import {createClient} from '@supabase/supabase-js';
const url=import.meta.env.VITE_SUPABASE_URL,key=import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
export const supabase=url&&key?createClient(url,key,{auth:{flowType:'pkce',persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}}):null;
export async function verifiedUser(){if(!supabase)return null;const {data,error}=await supabase.auth.getUser();if(error)return null;return data.user}
export const callbackURL=()=>location.origin+location.pathname;
export function isProtected(route){return ['workspace','plans'].includes(route)}
