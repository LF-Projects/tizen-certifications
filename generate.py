#!/usr/bin/env python3

# Copyright The Linux Foundation

import os
import yaml
from pprint import pprint
from PyPDF2 import PdfFileMerger, PdfFileReader
from fpdf import FPDF

with open ('config.yml') as certs_yaml:
  all_certifications = yaml.full_load(certs_yaml)

for config,config_data in all_certifications.items():

  if not config == 'certifications':
    print('Attempted to read invalid block "%s", skipping' % config)
    continue

  for certification in config_data:

    # Step through the derivatives

    print('\n%s - %s - Tizen %s - %s' % (
        certification['chipset'],
        certification['platform'],
        certification['version'],
        certification['original-cert-date']))

    number_derivatives = 0

    # Set up the source certification PDF
    merged_pdf = PdfFileMerger()
    merged_pdf.append(os.path.join('source-pdfs',certification['signed-cert-pdf']))

    # If there is a base model, there are derivatives
    if 'base-model' in certification and certification['base-model']:

      # Set up the derivative PDF formatting
      pdf = FPDF('P','in','Letter')
      pdf.set_margins(1,.75,1)
      pdf.add_page()

      # Add a title and subtitle
      pdf.set_font('Arial','b',24)
      pdf.cell(0,.65,'%s %s Derivatives' % (certification['chipset'],certification['platform']), 0, 2, 'C')
      pdf.set_font('Arial','b',20)
      pdf.cell(0,.35,'Tizen %s' % certification['version'], 0, 2, 'C')

      # Indicate the base model
      pdf.ln(.75)
      pdf.set_font('Arial','B',16)
      pdf.cell(0,.5,'Base Model (certified %s)' % certification['original-cert-date'], 0, 1, 'L')

      pdf.set_font('Arial','',12)
      pdf.cell(0,.25,certification['base-model'], 0, 1, 'L')
      pdf.set_font('Arial','',12)

      # Print out any derivatives
      for derivative in certification['derivatives']:

        pdf.ln(.75)

        pdf.set_font('Arial','B',16)
        pdf.cell(0,.5,'%s Models' % derivative['year'], 0, 1, 'L')

        pdf.ln(.25)

        # If there's a legend, print it
        if 'legend' in derivative and derivative['legend']:
          if derivative['legend']['sample']:

            pdf.set_font('Arial','B',14)
            pdf.cell(4,.35,'%s » %s' % (
                derivative['legend']['sample'],
                derivative['legend']['abbreviation']), 1, 2, 'C')
            pdf.set_font('Arial','',12)

            for reference_map in derivative['legend']['reference']:

              [(abbreviation, definition)] = reference_map.items()

              pdf.cell(1,.25,abbreviation, 1, 0, 'C')
              pdf.cell(3,.25,definition, 1, 1, 'L')

            pdf.ln(.5)

        pdf.set_font('Arial','',12)

        # Print the models
        if 'models' in derivative and derivative['models']:

          number_derivatives += len(set(derivative['models']))
          newline = True

          for model in sorted(set(derivative['models'])):
            if newline:
              pdf.cell(3.5,.25," - %s" % model, 0, 0, 'L')
              newline = False
            else:
              pdf.cell(3,.25," - %s" % model, 0, 1, 'L')
              newline = True

        else:
          pdf.cell(0,.25,'None specified', 0, 1, 'L')

      # Create a temporary PDF and add it to the certification PDF
      pdf.output('.derivatives.tmp','F').encode('latin-1')
      merged_pdf.append('.derivatives.tmp')

      print('   %s derivatives' % number_derivatives)

    else:
      print('   No derivatives')

    derivatives_clause = ''

    if number_derivatives:
      derivatives_clause = ' (%s derivatives)' % number_derivatives

    # Create the filename
    output_file = os.path.join('certifications',certification['chipset'],'%s - %s - Tizen %s - %s%s.pdf' % (
        certification['chipset'],
        certification['platform'],
        certification['version'],
        certification['original-cert-date'],
        derivatives_clause))

    # Make sure the target directory exists
    if not os.path.exists(os.path.join('certifications',certification['chipset'])):
      os.makedirs(os.path.join('certifications',certification['chipset']))

    # Write the PDF
    merged_pdf.write(output_file)
    print(' » %s\n' % output_file)

