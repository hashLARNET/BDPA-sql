/*
  # Crear buckets de Storage para archivos

  1. Buckets
    - `avances-fotos` - Para fotos de avances
    - `mediciones-docs` - Para documentos de mediciones

  2. Políticas de Storage
    - Usuarios autenticados pueden subir archivos
    - Usuarios autenticados pueden ver archivos
    - Solo propietarios pueden eliminar archivos
*/

-- Crear bucket para fotos de avances
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'avances-fotos',
  'avances-fotos',
  true,
  10485760, -- 10MB
  ARRAY['image/jpeg', 'image/png', 'image/webp']
) ON CONFLICT (id) DO NOTHING;

-- Crear bucket para documentos de mediciones
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'mediciones-docs',
  'mediciones-docs',
  true,
  52428800, -- 50MB
  ARRAY['application/pdf', 'image/jpeg', 'image/png', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
) ON CONFLICT (id) DO NOTHING;

-- Políticas para bucket avances-fotos
CREATE POLICY "Usuarios autenticados pueden ver fotos de avances"
  ON storage.objects
  FOR SELECT
  TO authenticated
  USING (bucket_id = 'avances-fotos');

CREATE POLICY "Usuarios autenticados pueden subir fotos de avances"
  ON storage.objects
  FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id = 'avances-fotos' 
    AND auth.uid() IS NOT NULL
  );

CREATE POLICY "Usuarios pueden actualizar sus propias fotos de avances"
  ON storage.objects
  FOR UPDATE
  TO authenticated
  USING (
    bucket_id = 'avances-fotos' 
    AND auth.uid()::text = owner::text
  );

CREATE POLICY "Usuarios pueden eliminar sus propias fotos de avances"
  ON storage.objects
  FOR DELETE
  TO authenticated
  USING (
    bucket_id = 'avances-fotos' 
    AND auth.uid()::text = owner::text
  );

-- Políticas para bucket mediciones-docs
CREATE POLICY "Usuarios autenticados pueden ver documentos de mediciones"
  ON storage.objects
  FOR SELECT
  TO authenticated
  USING (bucket_id = 'mediciones-docs');

CREATE POLICY "Usuarios autenticados pueden subir documentos de mediciones"
  ON storage.objects
  FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id = 'mediciones-docs' 
    AND auth.uid() IS NOT NULL
  );

CREATE POLICY "Usuarios pueden actualizar sus propios documentos de mediciones"
  ON storage.objects
  FOR UPDATE
  TO authenticated
  USING (
    bucket_id = 'mediciones-docs' 
    AND auth.uid()::text = owner::text
  );

CREATE POLICY "Usuarios pueden eliminar sus propios documentos de mediciones"
  ON storage.objects
  FOR DELETE
  TO authenticated
  USING (
    bucket_id = 'mediciones-docs' 
    AND auth.uid()::text = owner::text
  );