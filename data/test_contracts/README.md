# Imágenes de prueba

Este directorio contiene 3 pares de contratos simulados para probar el pipeline LegalMove.

## Caso 1 - Software
- `caso_1_software/documento_1__original.jpg`
- `caso_1_software/documento_1__enmienda.jpg`
- Cambios esperados: plazo 12→24 meses, pago USD 12.000→USD 15.000, soporte email→email+chat, terminación 30→60 días, nueva cláusula Protección de Datos.

## Caso 2 - Consultoría
- `caso_2_consultoria/documento_2__original.jpg`
- `caso_2_consultoria/documento_2__enmienda.jpg`
- Cambios esperados: agregado análisis regulatorio, duración 6→9 meses, honorarios USD 8.000→USD 9.500, entregables mensuales→quincenales, nueva cláusula Propiedad Intelectual.

## Caso 3 - SaaS
- `caso_3_saas/documento_3__original.jpg`
- `caso_3_saas/documento_3__enmienda.jpg`
- Cambios esperados: precio USD 1.200→USD 1.250, disponibilidad 99,5%→99,9%, soporte email→email+ticket.

`expected_changes.json` contiene la salida esperada aproximada para control funcional.
