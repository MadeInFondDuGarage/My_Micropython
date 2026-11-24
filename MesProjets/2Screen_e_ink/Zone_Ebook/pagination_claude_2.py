# html_reader.py — lecteur HTML pour MicroPython / ESP32

_SKIP_TAGS  = {"script", "style", "head"}
_BREAK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
               "li", "tr", "blockquote"}


class Reader:

    def __init__(self, path, chars=30, lines=15, n_pages=1):
        self.path    = path
        self.chars   = chars
        self.lines   = lines
        self._n      = n_pages  # pages chargées en mémoire
        self._text   = ""       # texte nettoyé
        self._hist   = [0]      # indices dans _text, un par page
        self._pos    = 0        # indice courant dans _hist
        self.pages   = []       # pages courantes (list of list of str)
        self.eof     = False
        self._load()

    # ------------------------------------------------------------------
    # API publique

    def next(self):
        if self.eof:
            return False
        self._pos += self._n
        self._build_pages()
        return True

    def prev(self):
        if self._pos == 0:
            return False
        self._pos = max(0, self._pos - self._n)
        self._build_pages()
        return True

    def goto_page(self, page_num):
        self._pos = max(0, min(page_num, len(self._hist) - 1))
        self._build_pages()

    def page_count(self):
        return len(self._hist)

    def current_page(self):
        return self._pos

    def save_position(self):
        return self._hist[self._pos]

    def restore_position(self, idx):
        """Reprend à un indice texte sauvegardé."""
        self._pos = 0
        self._hist = [0]
        if idx > 0:
            self._hist.append(idx)
            self._pos = 1
        self._build_pages()

    def save_index(self):
        import struct
        return struct.pack(">" + "I" * len(self._hist), *self._hist)

    def load_index(self, data):
        import struct
        n = len(data) // 4
        self._hist = list(struct.unpack(">" + "I" * n, data))
        self._pos  = 0
        self._build_pages()

    # ------------------------------------------------------------------
    # Chargement : parse HTML puis construit l'index complet

    def _load(self):
        self._text = self._parse_html()
        self._build_index()
        self._build_pages()

    # ------------------------------------------------------------------
    # Étape 1 : parse HTML → string propre

    def _parse_html(self):
        result     = []
        in_tag     = False
        tag_buf    = ""
        skip_depth = 0
        pending    = ""

        f = open(self.path, "r")
        raw = f.read()
        f.close()

        for ch in raw:
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
                            # saut de paragraphe : on flush le pending et on marque
                            word = pending.strip()
                            pending = ""
                            if word:
                                result.append(word)
                            result.append("\n")
                        elif skip_depth == 0 and bare == "br":
                            result.append("\n")
                else:
                    tag_buf += ch
            elif ch == "<":
                in_tag  = True
                tag_buf = ""
                # flush le pending accumulé
                if skip_depth == 0 and pending.strip():
                    result.append(pending.strip())
                    result.append(" ")
                pending = ""
            else:
                if skip_depth > 0:
                    continue
                pending += " " if ch in "\n\r\t" else ch

        if pending.strip():
            result.append(pending.strip())

        return "".join(result)

    # ------------------------------------------------------------------
    # Étape 2 : index — une entrée par page dans _text

    def _build_index(self):
        self._hist = []
        idx        = 0
        n          = len(self._text)

        while idx < n:
            self._hist.append(idx)
            idx = self._next_page_start(idx)

    def _next_page_start(self, start):
        """Retourne l'indice de début de la page suivante."""
        idx   = start
        lines = 0
        n     = len(self._text)

        while idx < n and lines < self.lines:
            # cherche fin de ligne naturelle (\n) ou wrap
            eol = self._text.find("\n", idx)
            if eol == -1:
                eol = n

            segment = self._text[idx:eol].strip()
            idx = eol + 1  # saute le \n

            if not segment:
                continue

            # compte les lignes que ce segment va produire après wrap
            while segment:
                lines += 1
                if lines >= self.lines:
                    break
                if len(segment) <= self.chars:
                    break
                cut = segment.rfind(" ", 0, self.chars)
                if cut <= 0:
                    cut = self.chars
                segment = segment[cut:].lstrip()

        return idx

    # ------------------------------------------------------------------
    # Étape 3 : construction des pages courantes

    def _build_pages(self):
        self.pages = []
        self.eof   = False

        for p in range(self._n):
            pos_idx = self._pos + p
            if pos_idx >= len(self._hist):
                self.eof = True
                break
            start = self._hist[pos_idx]
            end   = self._hist[pos_idx + 1] if pos_idx + 1 < len(self._hist) else len(self._text)
            self.pages.append(self._render_page(start, end))

        if self._pos + self._n >= len(self._hist):
            self.eof = True

    def _render_page(self, start, end):
        """Transforme un segment de _text en liste de strings wrappées."""
        page    = []
        segment = self._text[start:end]

        for para in segment.split("\n"):
            para = para.strip()
            if not para:
                continue
            while para:
                if len(para) <= self.chars:
                    page.append(para)
                    break
                cut = para.rfind(" ", 0, self.chars)
                if cut <= 0:
                    cut = self.chars
                page.append(para[:cut])
                para = para[cut:].lstrip()

        return page