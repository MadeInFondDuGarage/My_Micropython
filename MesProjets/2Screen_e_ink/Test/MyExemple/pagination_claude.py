# html_reader.py — lecteur HTML streaming pour MicroPython / ESP32

_SKIP_TAGS  = {"script", "style", "head"}
_BREAK_TAGS = {"p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6",
               "li", "tr", "blockquote"}


class Reader:

    def __init__(self, path, chars=30, lines=15, n_pages=1, chunk=512):
        self.path    = path
        self.chars   = chars
        self.lines   = lines
        self.chunk   = chunk
        self._n      = n_pages  # nombre de pages gardées en mémoire
        self._hist   = [0]      # offsets page par page (grandit avec next ou build_index)
        self._pos    = 0        # indice dans _hist (toujours en unité de 1 page)
        self.pages   = []       # n_pages pages courantes
        self.eof     = False
        self._indexed = False
        self._parse(self._n)

    # ------------------------------------------------------------------
    # API publique

    def next(self):
        """Avance de _n pages. Retourne False si fin de fichier."""
        if self.eof:
            return False
        self._pos += self._n
        self._parse(self._n)
        return True

    def prev(self):
        """Recule de _n pages. Retourne False si déjà au début."""
        if self._pos == 0:
            return False
        self._pos = max(0, self._pos - self._n)
        self._parse(self._n)
        return True

    def goto_page(self, page_num):
        """Saute à une page absolue (0-indexé). Nécessite build_index()."""
        if not self._indexed:
            raise Exception("build_index() requis")
        self._pos = max(0, min(page_num, len(self._hist) - 1))
        self._parse(self._n)

    def build_index(self):
        """Parcourt tout le fichier et remplit _hist avec un offset par page.
           Appelé une fois à l'ouverture. Peut être persisté/restauré."""
        self._hist    = [0]
        self._pos     = 0
        self.eof      = False
        file_offset   = 0

        page_chars  = 0   # chars dans la ligne courante
        page_lines  = 0   # lignes validées dans la page courante
        cur_line    = ""
        pending     = ""
        in_tag      = False
        tag_buf     = ""
        skip_depth  = 0

        f = open(self.path, "r")

        def _index_flush(force_break):
            nonlocal page_lines, cur_line, pending
            combined = (cur_line + " " + pending).strip() if cur_line else pending.strip()
            pending  = ""
            if not combined:
                return False
            wrapped = self._wrap(combined)
            for i, ln in enumerate(wrapped):
                is_last = (i == len(wrapped) - 1)
                if not is_last or force_break:
                    page_lines += 1
                    cur_line = ""
                    if page_lines >= self.lines:
                        return True
                else:
                    cur_line = ln
            return False

        while True:
            chunk = f.read(self.chunk)
            if not chunk:
                self.eof = True
                break

            for i, ch in enumerate(chunk):
                if in_tag:
                    if ch == ">":
                        in_tag  = False
                        tag     = tag_buf.strip().lower()
                        tag_buf = ""
                        closing = tag.startswith("/")
                        bare    = tag.lstrip("/").split()[0] if tag else ""
                        if closing:
                            if bare in _SKIP_TAGS and skip_depth > 0:
                                skip_depth -= 1
                        else:
                            if bare in _SKIP_TAGS:
                                skip_depth += 1
                            elif skip_depth == 0 and bare in _BREAK_TAGS:
                                if _index_flush(True):
                                    page_lines = 0
                                    cur_line   = ""
                                    self._hist.append(file_offset + i + 1)
                    else:
                        tag_buf += ch
                elif ch == "<":
                    in_tag  = True
                    tag_buf = ""
                    if skip_depth == 0 and len(pending) > self.chars * 2:
                        if _index_flush(False):
                            page_lines = 0
                            cur_line   = ""
                            self._hist.append(file_offset + i)
                else:
                    if skip_depth > 0:
                        continue
                    pending += " " if ch in "\n\r\t" else ch

            file_offset += len(chunk)

        f.close()
        self._indexed = True
        self._parse(self._n)

    def page_count(self):
        """Nombre total de pages (nécessite build_index())."""
        if not self._indexed:
            raise Exception("build_index() requis")
        return len(self._hist)

    def current_page(self):
        """Indice de la page courante (0-indexé)."""
        return self._pos

    def save_position(self):
        return self._hist[self._pos]

    def restore_position(self, offset):
        self._hist = [0]
        if offset > 0:
            self._hist.append(offset)
            self._pos = 1
        else:
            self._pos = 0
        self._indexed = False
        self._parse(self._n)

    def save_index(self):
        """Retourne _hist sous forme de bytes pour persistance."""
        import struct
        return struct.pack(">" + "I" * len(self._hist), *self._hist)

    def load_index(self, data):
        """Restaure _hist depuis les bytes sauvegardés."""
        import struct
        n = len(data) // 4
        self._hist    = list(struct.unpack(">" + "I" * n, data))
        self._pos     = 0
        self._indexed = True
        self._parse(self._n)

    # ------------------------------------------------------------------
    # Wrap

    def _wrap(self, text):
        result = []
        text   = text.strip()
        while len(text) > self.chars:
            cut = text.rfind(" ", 0, self.chars)
            if cut <= 0:
                cut = self.chars
            result.append(text[:cut])
            text = text[cut:].lstrip()
        if text:
            result.append(text)
        return result

    # ------------------------------------------------------------------
    # Flush

    def _flush(self, page, cur_line, pending, force_break):
        combined = (cur_line + " " + pending).strip() if cur_line else pending.strip()
        if not combined:
            return cur_line, False, ""
        wrapped = self._wrap(combined)
        for i, ln in enumerate(wrapped):
            is_last = (i == len(wrapped) - 1)
            if not is_last or force_break:
                page.append(ln)
                if len(page) >= self.lines:
                    # reste = lignes wrappées non encore poussées
                    reste = " ".join(wrapped[i + 1:])
                    return "", True, reste
            else:
                cur_line = ln
        return cur_line, False, ""

    # ------------------------------------------------------------------
    # Parser

    def _parse(self, n_pages):
        self.pages = []
        self.eof   = False
        file_offset = self._hist[self._pos]
        hist_idx    = self._pos

        f = open(self.path, "r")
        f.seek(file_offset)

        page       = []
        cur_line   = ""
        pending    = ""
        in_tag     = False
        tag_buf    = ""
        skip_depth = 0

        while len(self.pages) < n_pages:
            chunk = f.read(self.chunk)
            if not chunk:
                cur_line, _, reste = self._flush(page, cur_line, pending, True)
                if cur_line.strip():
                    page.append(cur_line.strip())
                if reste.strip():
                    page.append(reste.strip())
                if page:
                    self.pages.append(page)
                self.eof = True
                break

            for i, ch in enumerate(chunk):
                if in_tag:
                    if ch == ">":
                        in_tag  = False
                        tag     = tag_buf.strip().lower()
                        tag_buf = ""
                        closing = tag.startswith("/")
                        bare    = tag.lstrip("/").split()[0] if tag else ""
                        if closing:
                            if bare in _SKIP_TAGS and skip_depth > 0:
                                skip_depth -= 1
                        else:
                            if bare in _SKIP_TAGS:
                                skip_depth += 1
                            elif skip_depth == 0 and bare in _BREAK_TAGS:
                                cur_line, full, reste = self._flush(page, cur_line, pending, True)
                                pending = reste
                                if full:
                                    self.pages.append(page)
                                    stopped = file_offset + i + 1
                                    hist_idx += 1
                                    if not self._indexed:
                                        if hist_idx >= len(self._hist):
                                            self._hist.append(stopped)
                                        else:
                                            self._hist[hist_idx] = stopped
                                    if len(self.pages) >= n_pages:
                                        f.close()
                                        return
                                    page = []
                    else:
                        tag_buf += ch
                elif ch == "<":
                    in_tag  = True
                    tag_buf = ""
                    if skip_depth == 0 and len(pending) > self.chars * 2:
                        cur_line, full, reste = self._flush(page, cur_line, pending, False)
                        pending = reste
                        if full:
                            self.pages.append(page)
                            stopped = file_offset + i
                            hist_idx += 1
                            if not self._indexed:
                                if hist_idx >= len(self._hist):
                                    self._hist.append(stopped)
                                else:
                                    self._hist[hist_idx] = stopped
                            if len(self.pages) >= n_pages:
                                f.close()
                                return
                            page = []
                else:
                    if skip_depth > 0:
                        continue
                    pending += " " if ch in "\n\r\t" else ch

            file_offset += len(chunk)

        f.close()