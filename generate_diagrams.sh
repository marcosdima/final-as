#!/usr/bin/env bash
# ==============================================================================
# Script para generar imágenes a partir de archivos PlantUML (.puml)
# Repositorio: Análisis 2 - Casos de Uso
# ==============================================================================

set -euo pipefail

# Colores para salida por terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directorio raíz del proyecto (donde reside este script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuración por defecto
DEFAULT_OUTPUT_DIR="output"
OUTPUT_DIR=""
FORMAT="png"
VERBOSE=false
CLEAN=false
TARGET_INPUTS=()

# Variables para el ejecutor de PlantUML
RUNNER_TYPE=""
RUNNER_CMD=()
RUNNER_DESC=""

print_help() {
    cat << EOF
Uso: $(basename "$0") [OPCIONES] [ARCHIVOS_O_DIRECTORIOS...]

Ejecuta archivos PlantUML (.puml) y genera las imágenes correspondientes en la carpeta de salida.

OPCIONES:
    -o, --output <dir>      Directorio de salida. Si es relativo (por defecto: 'output'),
                            las imágenes se generan dentro de '<carpeta_origen>/<dir>'.
                            Si es una ruta absoluta o empieza con './', todas las imágenes
                            se generarán en ese directorio unificado.
    -f, --format <formato>  Formato de salida (png, svg, pdf, etc.). Por defecto: png.
    -c, --clean             Elimina las imágenes previamente generadas en el directorio de salida.
    -v, --verbose           Muestra salida detallada del proceso de generación.
    -h, --help              Muestra este mensaje de ayuda.

EJEMPLOS:
    # Genera todos los .puml del proyecto en sus respectivas carpetas output/ (ej. CU/output/):
    ./$(basename "$0")

    # Genera únicamente los .puml de la carpeta CU/:
    ./$(basename "$0") CU/

    # Genera un archivo específico:
    ./$(basename "$0") CU/01_seguridad_y_acceso.puml

    # Genera en formato SVG en una carpeta de salida global:
    ./$(basename "$0") -f svg -o ./diagramas_generados

EOF
}

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            print_help
            exit 0
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            echo -e "${RED}[ERROR] Opción no reconocida: $1${NC}" >&2
            print_help
            exit 1
            ;;
        *)
            TARGET_INPUTS+=("$1")
            shift
            ;;
    esac
done

# Resolver directorio de salida
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
fi

# Función para detectar cómo ejecutar PlantUML
detect_plantuml_runner() {
    # 1. Variable de entorno PLANTUML_JAR explícita
    if [[ -n "${PLANTUML_JAR:-}" && -f "$PLANTUML_JAR" ]]; then
        RUNNER_TYPE="java"
        RUNNER_CMD=(java -jar "$PLANTUML_JAR")
        RUNNER_DESC="Java JAR (definido en \$PLANTUML_JAR: $PLANTUML_JAR)"
        return 0
    fi

    # 2. Comando plantuml en PATH
    if command -v plantuml >/dev/null 2>&1; then
        RUNNER_TYPE="cmd"
        RUNNER_CMD=(plantuml)
        RUNNER_DESC="Comando 'plantuml' instalado en el sistema ($(command -v plantuml))"
        return 0
    fi

    # 3. Búsqueda de plantuml.jar en extensiones de VS Code / Cursor / sistema
    local candidate_jars=(
        "$PROJECT_ROOT/plantuml.jar"
        "$HOME/.local/share/plantuml/plantuml.jar"
        /usr/share/plantuml/plantuml.jar
        /usr/local/share/plantuml/plantuml.jar
    )

    # Buscar también en extensiones jebbs.plantuml instaladas en VS Code
    while IFS= read -r jar_match; do
        if [[ -f "$jar_match" ]]; then
            candidate_jars+=("$jar_match")
        fi
    done < <(find "$HOME/.vscode/extensions" "$HOME/.vscode-server/extensions" "$HOME/.cursor/extensions" -maxdepth 3 -name "plantuml.jar" 2>/dev/null || true)

    if command -v java >/dev/null 2>&1; then
        for jar_path in "${candidate_jars[@]}"; do
            if [[ -f "$jar_path" ]]; then
                RUNNER_TYPE="java"
                RUNNER_CMD=(java -jar "$jar_path")
                RUNNER_DESC="Java con JAR encontrado en $jar_path"
                return 0
            fi
        done
    fi

    # 4. Docker si está instalado y el daemon corriendo
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        RUNNER_TYPE="docker"
        RUNNER_DESC="Contenedor Docker (plantuml/plantuml)"
        return 0
    fi

    # 5. Si Java está presente pero falta el jar, descargarlo automáticamente a ~/.local/share/plantuml/
    if command -v java >/dev/null 2>&1; then
        local dl_dir="$HOME/.local/share/plantuml"
        local dl_jar="$dl_dir/plantuml.jar"
        echo -e "${YELLOW}[!] Se detectó Java pero no se encontró plantuml.jar ni el binario 'plantuml'.${NC}"
        echo -e "${BLUE}[*] Descargando la última versión oficial de plantuml.jar en $dl_jar...${NC}"
        mkdir -p "$dl_dir"
        if command -v curl >/dev/null 2>&1; then
            curl -fsSL -o "$dl_jar" "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
        elif command -v wget >/dev/null 2>&1; then
            wget -q -O "$dl_jar" "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
        fi

        if [[ -f "$dl_jar" && -s "$dl_jar" ]]; then
            RUNNER_TYPE="java"
            RUNNER_CMD=(java -jar "$dl_jar")
            RUNNER_DESC="Java con JAR descargado ($dl_jar)"
            return 0
        fi
    fi

    return 1
}

# Detectar motor
echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}        Generador de Diagramas PlantUML             ${NC}"
echo -e "${BLUE}====================================================${NC}"

if ! detect_plantuml_runner; then
    echo -e "${RED}[ERROR] No se encontró una forma de ejecutar PlantUML.${NC}" >&2
    echo -e "Opciones para solucionarlo:" >&2
    echo -e "  1. Instalar PlantUML: sudo apt install plantuml graphviz" >&2
    echo -e "  2. O definir la ruta al jar: export PLANTUML_JAR=/ruta/a/plantuml.jar" >&2
    echo -e "  3. O tener Docker activo." >&2
    exit 1
fi

echo -e "${CYAN}[INFO] Motor detectado:${NC} $RUNNER_DESC"
echo -e "${CYAN}[INFO] Formato de imagen:${NC} $FORMAT"
echo -e "${CYAN}[INFO] Destino:${NC} $OUTPUT_DIR"

# Recolectar archivos .puml
PUML_FILES=()

if [[ ${#TARGET_INPUTS[@]} -eq 0 ]]; then
    # Buscar todos los .puml excluyendo .git
    while IFS= read -r file; do
        PUML_FILES+=("$file")
    done < <(find "$PROJECT_ROOT" -name "*.puml" -not -path "*/.*/*" | sort)
else
    for input in "${TARGET_INPUTS[@]}"; do
        if [[ -d "$input" ]]; then
            while IFS= read -r file; do
                PUML_FILES+=("$file")
            done < <(find "$input" -name "*.puml" -not -path "*/.*/*" | sort)
        elif [[ -f "$input" ]]; then
            if [[ "$input" == *.puml ]]; then
                PUML_FILES+=("$input")
            else
                echo -e "${YELLOW}[!] Omitiendo archivo sin extensión .puml: $input${NC}"
            fi
        else
            echo -e "${RED}[ERROR] No existe el archivo o directorio especificado: $input${NC}" >&2
            exit 1
        fi
    done
fi

if [[ ${#PUML_FILES[@]} -eq 0 ]]; then
    echo -e "${YELLOW}[!] No se encontraron archivos .puml para procesar.${NC}"
    exit 0
fi

echo -e "${CYAN}[INFO] Archivos encontrados (${#PUML_FILES[@]}):${NC}"
for file in "${PUML_FILES[@]}"; do
    rel_path="${file#$PROJECT_ROOT/}"
    echo -e "   • $rel_path"
done

# Opción de limpieza previa
if [[ "$CLEAN" = true ]]; then
    echo -e "${YELLOW}[*] Limpiando imágenes anteriores en carpetas '$OUTPUT_DIR'...${NC}"
    for file in "${PUML_FILES[@]}"; do
        puml_dir="$(cd "$(dirname "$file")" && pwd)"
        target_clean_dir="$puml_dir/$OUTPUT_DIR"
        if [[ -d "$target_clean_dir" ]]; then
            rm -f "$target_clean_dir"/*."$FORMAT"
        fi
    done
fi

echo -e "\n${BLUE}[*] Generando diagramas...${NC}"

# Ejecutar generación
SUCCESS_COUNT=0
FAIL_COUNT=0

for file in "${PUML_FILES[@]}"; do
    filename="$(basename "$file")"
    file_dir="$(cd "$(dirname "$file")" && pwd)"
    rel_file="${file#$PROJECT_ROOT/}"

    # Si OUTPUT_DIR es relativo y no empieza con '.', PlantUML lo sitúa en <file_dir>/$OUTPUT_DIR
    # Si OUTPUT_DIR es una ruta absoluta o comienza con './', unificamos el destino
    actual_output_arg="$OUTPUT_DIR"
    if [[ "$OUTPUT_DIR" = /* ]]; then
        actual_output_arg="$OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
    elif [[ "$OUTPUT_DIR" == ./* ]]; then
        resolved_out="$(cd "$PROJECT_ROOT" && mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd)"
        actual_output_arg="$resolved_out"
    else
        mkdir -p "$file_dir/$OUTPUT_DIR"
    fi

    echo -ne "   Generando ${CYAN}$rel_file${NC}... "

    set +e
    if [[ "$RUNNER_TYPE" == "docker" ]]; then
        docker_cmd=(
            docker run --rm
            -v "$PROJECT_ROOT:/work"
            -w /work
            plantuml/plantuml
            -t"$FORMAT"
            -o "$actual_output_arg"
            "$rel_file"
        )
        if [[ "$VERBOSE" = true ]]; then
            echo ""
            "${docker_cmd[@]}"
            CMD_EXIT=$?
        else
            output_log="$("${docker_cmd[@]}" 2>&1)"
            CMD_EXIT=$?
        fi
    else
        extra_flags=(-t"$FORMAT" -o "$actual_output_arg")
        if [[ "$VERBOSE" = true ]]; then
            extra_flags+=(-v)
            echo ""
            "${RUNNER_CMD[@]}" "${extra_flags[@]}" "$file"
            CMD_EXIT=$?
        else
            output_log="$("${RUNNER_CMD[@]}" "${extra_flags[@]}" "$file" 2>&1)"
            CMD_EXIT=$?
        fi
    fi
    set -e

    if [[ $CMD_EXIT -eq 0 ]]; then
        echo -e "${GREEN}[OK]${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}[FALLÓ]${NC}"
        if [[ "$VERBOSE" = false && -n "${output_log:-}" ]]; then
            echo -e "${RED}$output_log${NC}"
        fi
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

echo -e "\n${BLUE}====================================================${NC}"
if [[ $FAIL_COUNT -eq 0 ]]; then
    echo -e "${GREEN}[✓] Proceso completado exitosamente: $SUCCESS_COUNT diagramas generados.${NC}"
    exit 0
else
    echo -e "${RED}[✗] Proceso finalizado con errores: $SUCCESS_COUNT exitosos, $FAIL_COUNT fallidos.${NC}"
    exit 1
fi
