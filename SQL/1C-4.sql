DECLATE @DT DATE;
SET @DT = '2022-05-01';
SELECT 
	--����� �
	(SELECT	FARMNUMBER FROM	BEDRIJF), 
	--�������� �����
	(SELECT	NAMEFARMER FROM	BEDRIJF),
	--���� ������
	CAST(DELIVERED_TIME AS DATE),
	--��� �������
	DS_RATION.DISPLAY_NAME,
	--������
	DS_RATION.DESCRIPTION,
	--������
	DS_GROUP.DESCRIPTION,
	--��� ������
	(SELECT	DS_GROUP_TYPE.NAME FROM DS_GROUP_TYPE WHERE DS_GROUP_TYPE.ID = DS_GROUP.GROUP_TYPE), 
	--���������
	DS_BATCH_DELIVERY.HEAD_COUNT HCD,
	--�����������ID
	DS_INGREDIENT.EXTERNAL_ID,
	--����������
	DS_INGREDIENT.DESCRIPTION dsID,
	--�������. ���/������
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/DS_BATCH_delivery.HEAD_COUNT,2),
	--����������� ���/������
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/DS_BATCH_delivery.HEAD_COUNT,2),
	--�������.���
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id),2),
	--����������� ���
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id),2),
	--��������� ���
	round(DS_BATCH_LOAD.LOADED_WEIGHT*(DS_BATCH_DELIVERY.DELIVERED_WEIGHT/NULLIF(DS_BATCH_DELIVERY.CALL_WEIGHT,0))/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id),2),
	--����. ���. ���/������
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--����������� ���. ���/������
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--����. ���. ���
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--����������� ���. ���
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--��������� ���. ���
	round(DS_BATCH_LOAD.LOADED_WEIGHT*(DS_BATCH_DELIVERY.DELIVERED_WEIGHT/NULLIF(DS_BATCH_DELIVERY.CALL_WEIGHT,0))/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--����������� ������ �������� / ������
	round(DS_BATCH_LOAD.LOADED_WEIGHT*((DS_BATCH_DELIVERY.DELIVERED_WEIGHT-DS_BATCH_DELIVERY.WEIGHBACK_AMOUNT)/NULLIF(DS_BATCH_DELIVERY.CALL_WEIGHT,0))/(SELECT sum(DS_BATCH_LOAD.LOADED_WEIGHT)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*(DS_BATCH_LOAD.DRYMATTER_PERC / 100)/DS_BATCH_delivery.HEAD_COUNT,2),
	--�����
	(SELECT ROUND(avg(DS_MILK.AMOUNT),0) FROM DS_MILK WHERE DS_MILK.GROUP_ID=DS_BATCH_DELIVERY.GROUP_ID AND CAST(ds_milk.MILK_DATE AS date)='2022-05-09') 
FROM DS_BATCH
INNER JOIN DS_RATION ON	DS_RATION.ID = DS_BATCH.RATION_ID
INNER JOIN DS_BATCH_LOAD ON	DS_BATCH_LOAD.BATCH_ID = DS_BATCH.ID
INNER JOIN DS_BATCH_DELIVERY ON	DS_BATCH_DELIVERY.BATCH_ID = DS_BATCH.ID 
INNER JOIN DS_GROUP ON	DS_GROUP.ID = DS_BATCH_DELIVERY.GROUP_ID 
INNER JOIN DS_INGREDIENT ON	DS_INGREDIENT.ID = DS_BATCH_LOAD.INGREDIENT_ID
WHERE CAST(DELIVERED_TIME AS DATE) = '2022-05-09'
	