SELECT 
    v.id,
	v.name AS vessel,
	v.email AS vsl_email,
	vdt.name AS document_name,
	vdc.name AS document_category,
	vd.updated_at,
	vd.expiration_date,
	vd.comments
FROM vessel_documents vd
LEFT JOIN parties p1
	on p1.id = vd.created_by_id
LEFT JOIN parties p2
	ON p2.id = vd.updated_by_id
LEFT JOIN vessel_document_types vdt
	ON vdt.id = vd.vessel_document_type_id
LEFT JOIN vessels v
	ON v.id = vd.vessel_id
LEFT JOIN vessel_document_categories vdc
	ON vdc.id = vdt.vessel_document_category_id
WHERE 
	v.active = 'true';
