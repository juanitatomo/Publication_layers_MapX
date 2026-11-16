<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>K1K2K3-MATRIX</sld:Name>
    <sld:UserStyle>
      <sld:Name>K1K2K3-MATRIX</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#FFFFFF" opacity="0" quantity="128" label=""/>
              <sld:ColorMapEntry color="#92f7d4" opacity="1.0" quantity="1" label="1) K1=0 K2=0 K3=0"/>
              <sld:ColorMapEntry color="#e50000" opacity="1.0" quantity="2" label="2) K1=0 K2=M K3=0"/>
              <sld:ColorMapEntry color="#fff700" opacity="1.0" quantity="3" label="3) K1=M K2=0 K3=0"/>
              <sld:ColorMapEntry color="#609ffc" opacity="1.0" quantity="4" label="4) K1=M K2=M K3=0"/>
              <sld:ColorMapEntry color="#ffb700" opacity="1.0" quantity="5" label="5) K1=0 K2=0 K3=M"/>
              <sld:ColorMapEntry color="#0061a6" opacity="1.0" quantity="6" label="6) K1=0 K2=M K3=M"/>
              <sld:ColorMapEntry color="#91ffff" opacity="1.0" quantity="7" label="7) K1=M K2=0 K3=M"/>
              <sld:ColorMapEntry color="#217a00" opacity="1.0" quantity="8" label="8) K1=M K2=M K3=M"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>