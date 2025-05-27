"""
DEX (Dalvik Executable) file format parser
Supports parsing and manipulation of Android DEX files
"""
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class DexHeader:
    """DEX file header structure"""
    magic: bytes
    version: str
    checksum: int
    signature: bytes
    file_size: int
    header_size: int
    endian_tag: int
    link_size: int
    link_off: int
    map_off: int
    string_ids_size: int
    string_ids_off: int
    type_ids_size: int
    type_ids_off: int
    proto_ids_size: int
    proto_ids_off: int
    field_ids_size: int
    field_ids_off: int
    method_ids_size: int
    method_ids_off: int
    class_defs_size: int
    class_defs_off: int
    data_size: int
    data_off: int


@dataclass
class DexStringId:
    """String ID item"""
    string_data_off: int
    string_data: str = ""


@dataclass
class DexTypeId:
    """Type ID item"""
    descriptor_idx: int
    descriptor: str = ""


@dataclass
class DexProtoId:
    """Prototype ID item"""
    shorty_idx: int
    return_type_idx: int
    parameters_off: int
    shorty: str = ""
    return_type: str = ""
    parameters: List[str] = None


@dataclass
class DexFieldId:
    """Field ID item"""
    class_idx: int
    type_idx: int
    name_idx: int
    class_name: str = ""
    type_name: str = ""
    field_name: str = ""


@dataclass
class DexMethodId:
    """Method ID item"""
    class_idx: int
    proto_idx: int
    name_idx: int
    class_name: str = ""
    prototype: str = ""
    method_name: str = ""


@dataclass
class DexClassDef:
    """Class definition item"""
    class_idx: int
    access_flags: int
    superclass_idx: int
    interfaces_off: int
    source_file_idx: int
    annotations_off: int
    class_data_off: int
    static_values_off: int
    class_name: str = ""
    superclass_name: str = ""
    source_file: str = ""


class DexParser:
    """Parser for DEX (Dalvik Executable) files"""
    
    DEX_MAGIC = b'dex\n'
    DEX_VERSIONS = [b'035\x00', b'037\x00', b'038\x00', b'039\x00']
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data = b''
        self.header: Optional[DexHeader] = None
        self.string_ids: List[DexStringId] = []
        self.type_ids: List[DexTypeId] = []
        self.proto_ids: List[DexProtoId] = []
        self.field_ids: List[DexFieldId] = []
        self.method_ids: List[DexMethodId] = []
        self.class_defs: List[DexClassDef] = []
        self.strings: List[str] = []
        
    def parse(self) -> bool:
        """Parse the DEX file"""
        try:
            with open(self.file_path, 'rb') as f:
                self.data = f.read()
            
            if not self._validate_magic():
                return False
                
            self._parse_header()
            self._parse_string_ids()
            self._parse_type_ids()
            self._parse_proto_ids()
            self._parse_field_ids()
            self._parse_method_ids()
            self._parse_class_defs()
            
            return True
            
        except Exception as e:
            print(f"Error parsing DEX file: {e}")
            return False
    
    def _validate_magic(self) -> bool:
        """Validate DEX magic number and version"""
        if len(self.data) < 8:
            return False
            
        magic = self.data[:4]
        version = self.data[4:8]
        
        return magic == self.DEX_MAGIC and version in self.DEX_VERSIONS
    
    def _parse_header(self):
        """Parse DEX header"""
        if len(self.data) < 112:  # Minimum header size
            raise ValueError("Invalid DEX file: header too short")
        
        # Unpack header fields
        header_data = struct.unpack('<8s I 20s 7I 8I', self.data[:112])
        
        magic_version = header_data[0]
        magic = magic_version[:4]
        version = magic_version[4:8].decode('ascii').rstrip('\x00')
        
        self.header = DexHeader(
            magic=magic,
            version=version,
            checksum=header_data[1],
            signature=header_data[2],
            file_size=header_data[3],
            header_size=header_data[4],
            endian_tag=header_data[5],
            link_size=header_data[6],
            link_off=header_data[7],
            map_off=header_data[8],
            string_ids_size=header_data[9],
            string_ids_off=header_data[10],
            type_ids_size=header_data[11],
            type_ids_off=header_data[12],
            proto_ids_size=header_data[13],
            proto_ids_off=header_data[14],
            field_ids_size=header_data[15],
            field_ids_off=header_data[16],
            method_ids_size=header_data[17],
            method_ids_off=header_data[18],
            class_defs_size=header_data[19],
            class_defs_off=header_data[20],
            data_size=header_data[21],
            data_off=header_data[22]
        )
    
    def _parse_string_ids(self):
        """Parse string ID table"""
        if not self.header or self.header.string_ids_size == 0:
            return
            
        offset = self.header.string_ids_off
        for i in range(self.header.string_ids_size):
            string_data_off = struct.unpack('<I', self.data[offset:offset+4])[0]
            string_id = DexStringId(string_data_off=string_data_off)
            
            # Read the actual string data
            string_data = self._read_string_data(string_data_off)
            string_id.string_data = string_data
            self.strings.append(string_data)
            
            self.string_ids.append(string_id)
            offset += 4
    
    def _read_string_data(self, offset: int) -> str:
        """Read string data from offset"""
        try:
            # Read ULEB128 length
            length, bytes_read = self._read_uleb128(offset)
            
            # Read string bytes
            string_start = offset + bytes_read
            string_bytes = self.data[string_start:string_start + length]
            
            # Decode as modified UTF-8
            return string_bytes.decode('utf-8', errors='replace')
            
        except Exception:
            return ""
    
    def _read_uleb128(self, offset: int) -> Tuple[int, int]:
        """Read ULEB128 encoded integer"""
        result = 0
        shift = 0
        bytes_read = 0
        
        while offset + bytes_read < len(self.data):
            byte = self.data[offset + bytes_read]
            bytes_read += 1
            
            result |= (byte & 0x7F) << shift
            
            if (byte & 0x80) == 0:
                break
                
            shift += 7
            
        return result, bytes_read
    
    def _parse_type_ids(self):
        """Parse type ID table"""
        if not self.header or self.header.type_ids_size == 0:
            return
            
        offset = self.header.type_ids_off
        for i in range(self.header.type_ids_size):
            descriptor_idx = struct.unpack('<I', self.data[offset:offset+4])[0]
            type_id = DexTypeId(descriptor_idx=descriptor_idx)
            
            if descriptor_idx < len(self.strings):
                type_id.descriptor = self.strings[descriptor_idx]
                
            self.type_ids.append(type_id)
            offset += 4
    
    def _parse_proto_ids(self):
        """Parse prototype ID table"""
        if not self.header or self.header.proto_ids_size == 0:
            return
            
        offset = self.header.proto_ids_off
        for i in range(self.header.proto_ids_size):
            shorty_idx, return_type_idx, parameters_off = struct.unpack('<3I', self.data[offset:offset+12])
            
            proto_id = DexProtoId(
                shorty_idx=shorty_idx,
                return_type_idx=return_type_idx,
                parameters_off=parameters_off,
                parameters=[]
            )
            
            if shorty_idx < len(self.strings):
                proto_id.shorty = self.strings[shorty_idx]
            if return_type_idx < len(self.type_ids):
                proto_id.return_type = self.type_ids[return_type_idx].descriptor
                
            self.proto_ids.append(proto_id)
            offset += 12
    
    def _parse_field_ids(self):
        """Parse field ID table"""
        if not self.header or self.header.field_ids_size == 0:
            return
            
        offset = self.header.field_ids_off
        for i in range(self.header.field_ids_size):
            class_idx, type_idx, name_idx = struct.unpack('<HHI', self.data[offset:offset+8])
            
            field_id = DexFieldId(
                class_idx=class_idx,
                type_idx=type_idx,
                name_idx=name_idx
            )
            
            if class_idx < len(self.type_ids):
                field_id.class_name = self.type_ids[class_idx].descriptor
            if type_idx < len(self.type_ids):
                field_id.type_name = self.type_ids[type_idx].descriptor
            if name_idx < len(self.strings):
                field_id.field_name = self.strings[name_idx]
                
            self.field_ids.append(field_id)
            offset += 8
    
    def _parse_method_ids(self):
        """Parse method ID table"""
        if not self.header or self.header.method_ids_size == 0:
            return
            
        offset = self.header.method_ids_off
        for i in range(self.header.method_ids_size):
            class_idx, proto_idx, name_idx = struct.unpack('<HHI', self.data[offset:offset+8])
            
            method_id = DexMethodId(
                class_idx=class_idx,
                proto_idx=proto_idx,
                name_idx=name_idx
            )
            
            if class_idx < len(self.type_ids):
                method_id.class_name = self.type_ids[class_idx].descriptor
            if proto_idx < len(self.proto_ids):
                method_id.prototype = self.proto_ids[proto_idx].shorty
            if name_idx < len(self.strings):
                method_id.method_name = self.strings[name_idx]
                
            self.method_ids.append(method_id)
            offset += 8
    
    def _parse_class_defs(self):
        """Parse class definition table"""
        if not self.header or self.header.class_defs_size == 0:
            return
            
        offset = self.header.class_defs_off
        for i in range(self.header.class_defs_size):
            class_data = struct.unpack('<8I', self.data[offset:offset+32])
            
            class_def = DexClassDef(
                class_idx=class_data[0],
                access_flags=class_data[1],
                superclass_idx=class_data[2],
                interfaces_off=class_data[3],
                source_file_idx=class_data[4],
                annotations_off=class_data[5],
                class_data_off=class_data[6],
                static_values_off=class_data[7]
            )
            
            if class_data[0] < len(self.type_ids):
                class_def.class_name = self.type_ids[class_data[0]].descriptor
            if class_data[2] != 0xFFFFFFFF and class_data[2] < len(self.type_ids):
                class_def.superclass_name = self.type_ids[class_data[2]].descriptor
            if class_data[4] != 0xFFFFFFFF and class_data[4] < len(self.strings):
                class_def.source_file = self.strings[class_data[4]]
                
            self.class_defs.append(class_def)
            offset += 32
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary information about the DEX file"""
        if not self.header:
            return {}
            
        return {
            'file_path': str(self.file_path),
            'version': self.header.version,
            'file_size': self.header.file_size,
            'checksum': hex(self.header.checksum),
            'strings_count': len(self.string_ids),
            'types_count': len(self.type_ids),
            'prototypes_count': len(self.proto_ids),
            'fields_count': len(self.field_ids),
            'methods_count': len(self.method_ids),
            'classes_count': len(self.class_defs)
        }
    
    def get_class_names(self) -> List[str]:
        """Get list of all class names"""
        return [class_def.class_name for class_def in self.class_defs if class_def.class_name]
    
    def get_method_names(self) -> List[str]:
        """Get list of all method names"""
        return [method_id.method_name for method_id in self.method_ids if method_id.method_name]
    
    def get_string_pool(self) -> List[str]:
        """Get the string pool"""
        return self.strings.copy()
