# Matriz de roles y permisos

## Reglas generales

- Los permisos Django se suman: el usuario obtiene los permisos directos de
  `user_permissions` y los permisos de todos sus grupos. Quitar un permiso de
  un grupo no revoca una concesión directa, y editar el grupo afecta a todos
  sus miembros.
- Las cuentas activas con `is_staff` o `is_superuser` tienen acceso completo
  a las acciones de gestión de esta aplicación. La asignación de grupos y
  permisos individuales también está reservada a estas cuentas.
- Una cuenta inactiva no obtiene acceso aunque sea staff, superusuario o
  miembro de un grupo con permisos. Las vistas de gestión usan la
  autorización del servidor, no solo los enlaces de navegación.
- En las tablas siguientes, `auth.view_*`, `auth.add_*`, `auth.change_*` y
  `auth.delete_*` indican el permiso requerido para ver, crear, editar y
  eliminar, respectivamente. Para las demás secciones se usa el mismo patrón
  con el prefijo y nombre de modelo indicados.
- Para cuentas parciales, cada acción requiere su permiso explícito. Tener
  `add` no concede `view`, `change` ni `delete`. Los permisos se evalúan también
  en solicitudes POST y al acceder directamente a una URL.

## Matriz de acciones por sección

| Sección | Ver | Crear | Editar | Eliminar |
|---|---|---|---|---|
| Usuarios (`auth.user`) | `auth.view_user` | `auth.add_user` | `auth.change_user` | `auth.delete_user` |
| Roles (`auth.group`) | `auth.view_group` | `auth.add_group` | `auth.change_group` | `auth.delete_group` |
| Permisos (`auth.permission`) | `auth.view_permission` | `auth.add_permission` | No hay acción de edición en la aplicación | No hay acción de eliminación en la aplicación |
| Perfiles (`usuarios.perfilusuario`) | `usuarios.view_perfilusuario` | `usuarios.add_perfilusuario` | `usuarios.change_perfilusuario` | `usuarios.delete_perfilusuario` |
| Evaluaciones de accesibilidad (`usuarios.evaluacionaccesibilidad`) | `usuarios.view_evaluacionaccesibilidad` | `usuarios.add_evaluacionaccesibilidad` | `usuarios.change_evaluacionaccesibilidad` | `usuarios.delete_evaluacionaccesibilidad` |
| Niveles del juego (`niveles.level`) | `niveles.view_level` | `niveles.add_level` | `niveles.change_level` | `niveles.delete_level` |
| Niveles (`niveles.nivel`) | `niveles.view_nivel` | `niveles.add_nivel` | `niveles.change_nivel` | `niveles.delete_nivel` |
| Progresos (`niveles.progreso`) | `niveles.view_progreso` | `niveles.add_progreso` | `niveles.change_progreso` | `niveles.delete_progreso` |
| Logros (`niveles.logro`) | `niveles.view_logro` | `niveles.add_logro` | `niveles.change_logro` | `niveles.delete_logro` |
| Logros de usuarios (`niveles.usuariologro`) | `niveles.view_usuariologro` | `niveles.add_usuariologro` | `niveles.change_usuariologro` | `niveles.delete_usuariologro` |

## Matriz de actores

| Actor | Ver | Crear | Editar | Eliminar | Asignar grupos/permisos |
|---|---|---|---|---|---|
| Administrador activo (`is_staff` o `is_superuser`) | Todas las secciones con vista implementada | Todas las acciones de creación implementadas | Todas las acciones de edición implementadas | Todas las acciones de eliminación implementadas | Sí |
| Jugador sin permisos de gestión | Juego y su perfil propio; ninguna sección de gestión | No en gestión | No en gestión | No en gestión | No |
| Usuario activo sin permisos | Ninguna sección de gestión; las pantallas propias del juego siguen disponibles | No en gestión | No en gestión | No en gestión | No |
| Usuario activo con permisos parciales | Solo las secciones para las que tiene `view` o `add` | Solo con el `add` de la sección | Solo con el `change` de la sección | Solo con el `delete` de la sección | No |
| Cualquier usuario inactivo | Ninguna sección de gestión | No | No | No | No |

El jugador autenticado puede seguir usando las acciones de juego habilitadas
por las reglas del propio juego. No son permisos de CRUD administrativo y no
aparecen como acceso a secciones de gestión en esta matriz.

## Cobertura y límites

- Las rutas de CRUD de usuarios, perfiles, evaluaciones, niveles, progresos y
  logros comprueban permisos en el servidor.
- La asignación de grupos y permisos individuales está limitada a
  administradores activos y modifica solo al usuario seleccionado; los
  permisos de su grupo compartido no se reescriben.
- Las vistas CRUD de datos con propietario limitan los registros visibles a
  los propios del usuario cuando este no es staff ni superusuario, incluso si
  tiene el permiso de modelo correspondiente.
- Los permisos personalizados `usuarios.can_reset_lives`,
  `usuarios.can_give_gems` y `niveles.can_design_levels` existen en los
  modelos, pero actualmente no corresponden a acciones de gestión expuestas
  por estas vistas.
- La autorización del API de juego se rige por su autenticación y reglas de
  juego, no por los permisos de gestión de Django.

No se requiere migración para esta matriz ni para las comprobaciones de
autorización.
