select 
    t2.name as VESSEL,
    t2.build_date as DELIVERY_DATE,
    max(case when t3.id = '793' then t1.expiration_date end) as Bottom_Survey_Afloat_UWILD,
    max(case when t3.id = '784' then t1.expiration_date end) as Bottom_Survey_Dry_Dock,
    max(case when t3.id = '733' then t1.expiration_date end) as Hull_Renewal
from vessel_documents t1
inner join vessels t2
    on t2.id = t1.vessel_id
inner join vessel_document_types t3
    on t3.id = t1.vessel_document_type_id
where t3.id in ('793','784','733')
group by t2.name, t2.build_date
order by t2.name;