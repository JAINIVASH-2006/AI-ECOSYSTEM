-- Apply to the new EcoRestore project only. Owner policies enforce data access.
begin;
create table if not exists public.eco_plans (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 name text not null check(char_length(name) between 1 and 120),
 zone_id text not null check(char_length(zone_id) between 1 and 100),
 baseline_score numeric not null check(baseline_score between 0 and 100),
 scenario_score numeric not null check(scenario_score between 0 and 100),
 recovery_percent integer not null check(recovery_percent between 0 and 50),
 field_note text not null default '' check(char_length(field_note)<=2000),
 status text not null default 'draft' check(status in ('draft','field_review','verified')),
 source text not null default 'SYNTHETIC_DEMO',
 snapshot jsonb not null default '{}'::jsonb check(jsonb_typeof(snapshot)='object'),
 created_at timestamptz not null default now()
);
create index if not exists eco_plans_owner_created_idx on public.eco_plans(owner_id,created_at desc);
alter table public.eco_plans enable row level security;
revoke all on public.eco_plans from anon;
grant select,insert,update,delete on public.eco_plans to authenticated;
drop policy if exists eco_plans_select on public.eco_plans;
create policy eco_plans_select on public.eco_plans for select to authenticated using((select auth.uid())=owner_id);
drop policy if exists eco_plans_insert on public.eco_plans;
create policy eco_plans_insert on public.eco_plans for insert to authenticated with check((select auth.uid())=owner_id);
drop policy if exists eco_plans_update on public.eco_plans;
create policy eco_plans_update on public.eco_plans for update to authenticated using((select auth.uid())=owner_id) with check((select auth.uid())=owner_id);
drop policy if exists eco_plans_delete on public.eco_plans;
create policy eco_plans_delete on public.eco_plans for delete to authenticated using((select auth.uid())=owner_id);
commit;
