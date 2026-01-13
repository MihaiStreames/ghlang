use serde::Serialize;
use std::collections::HashMap;
use std::env;
use std::path::Path;
use std::process;
use tokei::{Config, Languages};

/// Per-language line statistics
#[derive(Serialize)]
struct LangStats {
    #[serde(rename = "nFiles")]
    n_files: usize,
    blank: usize,
    comment: usize,
    code: usize,
}

/// Structured error payload for stderr output
#[derive(Serialize)]
struct ErrorPayload {
    error: ErrorBody,
}

/// Error details emitted by tokount
#[derive(Serialize)]
struct ErrorBody {
    kind: String,
    message: String,
    details: Option<HashMap<String, String>>,
}

/// Emit a structured error payload to stderr and exit with a non-zero code
fn emit_error(kind: &str, message: &str, details: Option<HashMap<String, String>>) -> ! {
    let payload = ErrorPayload {
        error: ErrorBody {
            kind: kind.to_string(),
            message: message.to_string(),
            details,
        },
    };

    match serde_json::to_string(&payload) {
        Ok(json) => eprintln!("{json}"),
        Err(err) => {
            eprintln!("{{\"error\":{{\"kind\":\"SerializeError\",\"message\":\"{err}\"}}}}")
        }
    }

    process::exit(2);
}

/// Main entry point
fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        let mut details = HashMap::new();
        details.insert(
            "usage".to_string(),
            "tokount <path> [excluded_dir1,excluded_dir2,...]".to_string(),
        );
        emit_error(
            "InvalidArgs",
            "Missing required <path> argument",
            Some(details),
        );
    }

    let path = &args[1];
    let path_ref = Path::new(path);
    if !path_ref.exists() {
        emit_error("NotFound", "Path does not exist", None);
    }

    if let Err(err) = path_ref.metadata() {
        emit_error(
            "IoError",
            "Failed to read path metadata",
            Some({
                let mut details = HashMap::new();
                details.insert("error".to_string(), err.to_string());
                details
            }),
        );
    }

    let excluded: Vec<&str> = if args.len() > 2 {
        args[2].split(',').filter(|s| !s.is_empty()).collect()
    } else {
        vec![]
    };

    let config = Config::default();
    let mut languages = Languages::new();

    let path_ref: &[&str] = &[path];
    let excluded_ref: &[&str] = &excluded;

    languages.get_statistics(path_ref, excluded_ref, &config);

    let mut result: HashMap<String, LangStats> = HashMap::new();

    let mut total_files: usize = 0;
    let mut total_blank: usize = 0;
    let mut total_comment: usize = 0;
    let mut total_code: usize = 0;

    for (lang_type, lang) in languages.iter() {
        if lang.code > 0 {
            let file_count = lang.reports.len();

            result.insert(
                lang_type.name().to_string(),
                LangStats {
                    n_files: file_count,
                    blank: lang.blanks,
                    comment: lang.comments,
                    code: lang.code,
                },
            );

            total_files += file_count;
            total_blank += lang.blanks;
            total_comment += lang.comments;
            total_code += lang.code;
        }
    }

    result.insert(
        "SUM".to_string(),
        LangStats {
            n_files: total_files,
            blank: total_blank,
            comment: total_comment,
            code: total_code,
        },
    );

    println!("{}", serde_json::to_string(&result).unwrap());
}
