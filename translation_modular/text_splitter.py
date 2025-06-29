class TextSplitter:
    """Handles text splitting into chunks for translation"""
    
    def __init__(self):
        pass
    
    def split_text_into_chunks(self, input_text, source_lang, target_tokens=2048):
        """Split text into chunks of approximately target_tokens"""
        
        # Determine chunk size in characters based on token estimation
        chars_per_chunk = target_tokens * (3 if source_lang == 'hi' else 4)
        
        text_length = len(input_text)
        chunks = []
        current_pos = 0
        chunk_num = 1
        
        while current_pos < text_length:
            # Calculate end position for this chunk (or end of text)
            target_end = min(current_pos + int(chars_per_chunk), text_length)
            
            # If we're not at the end of the text, adjust to avoid breaking words
            if target_end < text_length:
                target_end = self._find_word_boundary(
                    input_text, target_end, current_pos, chars_per_chunk, chunk_num
                )
            
            # Extract the chunk and add to our list
            chunk = input_text[current_pos:target_end]
            chunks.append(chunk)
            
            # Update for next iteration
            current_pos = target_end
            chunk_num += 1
        
        return chunks
    
    def _find_word_boundary(self, input_text, target_end, current_pos, chars_per_chunk, chunk_num):
        """Find appropriate word boundary for chunk splitting"""
        text_length = len(input_text)
        word_boundary_found = False
        
        # Define search window: look back up to 200 chars from target
        search_start = max(current_pos + int(chars_per_chunk * 0.9), current_pos)
        search_end = min(current_pos + int(chars_per_chunk * 1.1), text_length)
        
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
