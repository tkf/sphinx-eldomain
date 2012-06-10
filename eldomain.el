;;; eldomain.el --- Generate data for eldomain

;; Copyright (C) 2012- Takafumi Arakaki

;; Author: Takafumi Arakaki

;; This file is NOT part of GNU Emacs.

;; eldomain is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; eldomain is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with eldomain.  If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:

;;

;;; Code:

(eval-when-compile (require 'cl))
(require 'help-fns)
(require 'json)

(defvar eldomain-prefix nil)

(defun eldomain-get-symbols (predicate)
  (loop for x being the symbols
        with regexp = (format "^%s" eldomain-prefix)
        if (and (funcall predicate  x)
                (string-match regexp (format "%S" x)))
        collect x))

(defun eldomain-get-function-data ()
  (loop for x in (eldomain-get-symbols #'fboundp)
        for name = (format "%S" x)
        for arg = (format "%S" (help-function-arglist x))
        for doc = (documentation x)
        collect `((name . ,name) (arg . ,arg) (doc . ,doc))))

(defun eldomain-get-variable-data ()
  (loop for x in (eldomain-get-symbols #'boundp)
        for name = (format "%S" x)
        for doc = (documentation-property x 'variable-documentation t)
        collect `((name . ,name) (doc . ,doc))))

(defun eldomain-get-face-data ()
  (loop for x in (eldomain-get-symbols #'facep)
        for name = (format "%S" x)
        for doc = (documentation-property x 'face-documentation t)
        collect `((name . ,name) (doc . ,doc))))

(defun eldomain-get-data ()
  `((function . ,(apply #'vector (eldomain-get-function-data)))
    (variable . ,(apply #'vector (eldomain-get-variable-data)))
    (face     . ,(apply #'vector (eldomain-get-face-data)))))

(defun eldomain-main ()
  (assert eldomain-prefix nil "`eldomain-prefix' must be set.")
  (princ (json-encode (eldomain-get-data)))
  (kill-emacs))

(eldomain-main)

;;; eldomain.el ends here
