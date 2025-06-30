class TextSplitter:
    """Handles text splitting into chunks for translation"""
    
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model for English text processing"""
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✓ spaCy model loaded successfully")
            except OSError:
                print("Downloading spaCy model 'en_core_web_sm'...")
                import spacy.cli
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
                print("✓ spaCy model downloaded and loaded successfully")
        except ImportError:
            print("⚠️  spaCy not installed. Install with: pip install spacy")
            print("   English splitting will use basic logic")
            self.nlp = None
    
    def split_text_into_chunks(self, input_text, source_lang, target_tokens=1024):
        """Split text into chunks of approximately target_tokens"""
        # Use spaCy-based splitting for English if available
        if source_lang == 'en' and self.nlp is not None:
            return self._split_english_with_spacy(input_text, target_tokens)
        else:
            return self._split_with_basic_logic(input_text, source_lang, target_tokens)
    
    def _split_english_with_spacy(self, input_text, target_tokens):
        """Split English text using spaCy for better sentence segmentation"""
        chars_per_chunk = target_tokens * 4  # Approximate chars per token for English
        
        doc = self.nlp(input_text)
        sentences = list(doc.sents)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sent in sentences:
            sent_text = sent.text.strip()
            sent_length = len(sent_text)
            
            # If adding this sentence would exceed the limit
            if current_length + sent_length > chars_per_chunk and current_chunk:
                # Finalize current chunk
                chunk_text = ' '.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                
                # Start new chunk with current sentence
                current_chunk = [sent_text]
                current_length = sent_length
            else:
                # Add sentence to current chunk
                current_chunk.append(sent_text)
                current_length += sent_length + 1  # +1 for space
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
        
        return chunks
    
    def _split_with_basic_logic(self, input_text, source_lang, target_tokens):
        """Original splitting logic for Hindi and fallback for English"""
        chars_per_chunk = target_tokens * (3 if source_lang == 'hi' else 4)

        text_length = len(input_text)
        chunks = []
        current_pos = 0
        chunk_num = 1

        while current_pos < text_length:
            target_end = min(current_pos + int(chars_per_chunk), text_length)

            if target_end < text_length:
                target_end = self._find_word_boundary(
                    input_text, target_end, current_pos, chars_per_chunk, chunk_num, source_lang
                )

            chunk = input_text[current_pos:target_end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            current_pos = target_end
            chunk_num += 1

        return chunks
    
    def _find_word_boundary(self, input_text, target_end, current_pos, chars_per_chunk, chunk_num, source_lang):
        """Find appropriate word boundary for chunk splitting"""
        text_length = len(input_text)
        word_boundary_found = False
        
        # Define search window: look back up to 200 chars from target
        search_start = max(current_pos + int(chars_per_chunk * 0.9), current_pos)
        search_end = min(current_pos + int(chars_per_chunk * 1.1), text_length)
        
        # For Hindi, prioritize splitting at | character
        if source_lang == 'hi':
            # Try to find | character within the search range
            for i in range(target_end, search_start, -1):
                if i < text_length and input_text[i] == '|':
                    return i + 1
            
            # Look forward for | character
            for i in range(target_end, search_end):
                if i < text_length and input_text[i] == '|':
                    return i + 1

        # Look for paragraph breaks first (most natural)
        for i in range(target_end, search_start, -1):
            if i < text_length and input_text[i-1:i+1] == '\n\n':
                target_end = i
                word_boundary_found = True
                break
        
        # If no paragraph break, look for sentence endings
        if not word_boundary_found:
            for i in range(target_end, search_start, -1):
                if i < text_length and input_text[i-1] in ['.', '!', '?', '।'] and (i == text_length or input_text[i] in [' ', '\n']):
                    target_end = i
                    word_boundary_found = True
                    break
        
        # If no sentence end, just find a space
        if not word_boundary_found:
            for i in range(target_end, search_start, -1):
                if i < text_length and input_text[i-1] in [' ', '\n', '\t']:
                    target_end = i
                    word_boundary_found = True
                    break
        
        # If still no boundary found, try to find one after the target point
        if not word_boundary_found:
            for i in range(target_end, search_end):
                if i < text_length and input_text[i] in [' ', '\n', '\t']:
                    target_end = i + 1
                    word_boundary_found = True
                    break
        
        # Last resort - just cut at target position
        # if not word_boundary_found: may break mid-word
        
        return target_end
